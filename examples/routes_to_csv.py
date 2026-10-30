"""Google Flights itineraries for several routes and the same dates, in one CSV.

    python routes_to_csv.py JFK-LAX MXP-LHR CDG-JFK --outbound 2026-12-01 --return 2026-12-04 --currency USD

Routes are written as FROM-TO with IATA codes. Each row keeps the route it
came from, its airline, times, duration, stops, price and CO2 estimate; the
script prints the cheapest itinerary of every route.
"""

import argparse

from quanticdata_google_flights_scraper import GoogleFlightsScraper, write


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("routes", nargs="+", help="FROM-TO pairs of IATA codes, e.g. JFK-LAX")
    parser.add_argument("--outbound", required=True, help="YYYY-MM-DD")
    parser.add_argument("--return", dest="return_date", help="YYYY-MM-DD; omit for one-way")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--max-results", type=int, default=15, help="itineraries per route (max 30)")
    parser.add_argument("--out", default="routes.csv")
    args = parser.parse_args()

    flights = GoogleFlightsScraper()
    rows = []
    for route in args.routes:
        departure, _, arrival = route.upper().partition("-")
        run = flights.search(departure, arrival_id=arrival, outbound_date=args.outbound,
                             return_date=args.return_date, currency=args.currency, max_results=args.max_results)
        priced = [f for f in run if f.get("price_value")]
        if priced:
            best = min(priced, key=lambda f: f["price_value"])
            print(f"{route}: {len(run)} itineraries, cheapest {best['price']} ({best['airline']}, {best['stops']})")
        else:
            print(f"{route}: {len(run)} itineraries")
        rows.extend({"route": route.upper(), **f} for f in run)

    write(rows, args.out)
    print(f"{len(rows)} itineraries written to {args.out}")


if __name__ == "__main__":
    main()
