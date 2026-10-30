"""Track the Google Flights fare of one trip over time.

Prices a route for fixed dates and appends one row to fare_history.csv with a
UTC timestamp, the cheapest fare and the cheapest nonstop fare (with their
airlines and departure times). Run it every day from cron and buy when the
price drops:

    0 9 * * *  cd /path/to/here && python fare_watch.py JFK LAX --outbound 2026-12-01 --return 2026-12-04

Needs a login (`google-flights-scraper login`) or QUANTICDATA_API_KEY in the environment.
"""

import argparse
import csv
import os
from datetime import datetime, timezone

from quanticdata_google_flights_scraper import GoogleFlightsScraper

FIELDS = ["checked_at", "departure_id", "arrival_id", "outbound_date", "return_date", "currency", "itineraries",
          "cheapest", "cheapest_airline", "cheapest_departure", "cheapest_nonstop", "nonstop_airline",
          "nonstop_departure"]


def cheapest(itineraries):
    priced = [f for f in itineraries if f.get("price_value")]
    return min(priced, key=lambda f: f["price_value"]) if priced else {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("departure", help="IATA code, e.g. JFK")
    parser.add_argument("arrival", help="IATA code, e.g. LAX")
    parser.add_argument("--outbound", required=True, help="YYYY-MM-DD")
    parser.add_argument("--return", dest="return_date", help="YYYY-MM-DD; omit for one-way")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--out", default="fare_history.csv")
    args = parser.parse_args()

    flights = GoogleFlightsScraper()
    run = flights.search(args.departure, arrival_id=args.arrival, outbound_date=args.outbound,
                         return_date=args.return_date, currency=args.currency, max_results=30)
    best = cheapest(run)
    nonstop = cheapest([f for f in run if f.get("stops_count") == 0])
    row = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "departure_id": args.departure.upper(),
        "arrival_id": args.arrival.upper(),
        "outbound_date": args.outbound,
        "return_date": args.return_date,
        "currency": args.currency,
        "itineraries": len(run),
        "cheapest": best.get("price_value"),
        "cheapest_airline": best.get("airline"),
        "cheapest_departure": best.get("departure_time"),
        "cheapest_nonstop": nonstop.get("price_value"),
        "nonstop_airline": nonstop.get("airline"),
        "nonstop_departure": nonstop.get("departure_time"),
    }

    new_file = not os.path.exists(args.out)
    with open(args.out, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    print(f"cheapest {row['cheapest']} {args.currency} ({row['cheapest_airline']}), "
          f"nonstop {row['cheapest_nonstop']} ({row['nonstop_airline']}), appended to {args.out}")


if __name__ == "__main__":
    main()
