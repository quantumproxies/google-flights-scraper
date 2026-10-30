"""Cheapest Google Flights fare of a route for each day of a date range.

    python fare_calendar.py JFK LAX --start 2026-12-01 --days 10 --trip-length 3 --currency USD

Prices the route on --days consecutive outbound dates. With --trip-length N
each search is a round trip that returns N days later; without it, one-way.
Writes one row per date with the number of itineraries, the cheapest fare and
the cheapest nonstop fare, and marks the cheapest day.
"""

import argparse
from datetime import date, timedelta

from quanticdata_google_flights_scraper import GoogleFlightsScraper, write


def cheapest(itineraries):
    priced = [f for f in itineraries if f.get("price_value")]
    return min(priced, key=lambda f: f["price_value"]) if priced else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("departure", help="IATA code, e.g. JFK")
    parser.add_argument("arrival", help="IATA code, e.g. LAX")
    parser.add_argument("--start", required=True, help="first outbound date, YYYY-MM-DD")
    parser.add_argument("--days", type=int, default=7, help="how many outbound dates to price")
    parser.add_argument("--trip-length", type=int, help="days until the return flight; omit for one-way")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--out", default="fare_calendar.csv")
    args = parser.parse_args()

    flights = GoogleFlightsScraper()
    start = date.fromisoformat(args.start)
    rows = []
    for i in range(args.days):
        outbound = start + timedelta(days=i)
        back = (outbound + timedelta(days=args.trip_length)).isoformat() if args.trip_length else None
        run = flights.search(args.departure, arrival_id=args.arrival, outbound_date=outbound.isoformat(),
                             return_date=back, currency=args.currency, max_results=30)
        best = cheapest(run)
        best_nonstop = cheapest([f for f in run if f.get("stops_count") == 0])
        rows.append({
            "outbound_date": outbound.isoformat(),
            "return_date": back,
            "itineraries": len(run),
            "cheapest": best["price_value"] if best else None,
            "cheapest_airline": best["airline"] if best else None,
            "cheapest_nonstop": best_nonstop["price_value"] if best_nonstop else None,
            "nonstop_airline": best_nonstop["airline"] if best_nonstop else None,
            "currency": args.currency,
        })
        print(f"{outbound}: cheapest {rows[-1]['cheapest']}, nonstop {rows[-1]['cheapest_nonstop']} {args.currency}")

    priced = [r for r in rows if r["cheapest"] is not None]
    if priced:
        low = min(priced, key=lambda r: r["cheapest"])
        print(f"cheapest day: {low['outbound_date']} at {low['cheapest']} {args.currency} ({low['cheapest_airline']})")
    write(rows, args.out)
    print(f"{len(rows)} dates written to {args.out}")


if __name__ == "__main__":
    main()
