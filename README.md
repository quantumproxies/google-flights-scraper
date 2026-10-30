# Google Flights Scraper

[![ci](https://github.com/quantumproxies/google-flights-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/quantumproxies/google-flights-scraper/actions/workflows/ci.yml) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

Scrape Google Flights from Python or the command line: the one-way or round-trip itineraries between two airports for the dates you choose, with airline, departure and arrival times, duration, stops, price and CO2 estimate, as JSON or CSV. The code is free and open source (MIT). It runs on the QuanticData Data API, so there are no proxies to rotate and no headless browser to keep alive: sign in once and run a command.

```bash
pip install git+https://github.com/quantumproxies/google-flights-scraper
google-flights-scraper login
google-flights-scraper search JFK --arrival-id LAX --outbound-date 2026-12-01 --return-date 2026-12-04 --currency USD -o jfk_lax.csv
```

`login` opens the QuanticData sign-in page in your browser. New accounts get $2 of free usage every month, no card required: [create one](https://app.quanticdata.io/register?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper).

## What it scrapes

| Command | Input | Returns | Per run |
|---|---|---|---|
| `google-flights-scraper search` | departure and arrival IATA codes, dates | Airline, times, stops, price, emissions, 20 fields per row ([fields and price](https://quanticdata.io/collectors/google-flights-api/?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper)) | up to 30 |

Give the departure code, `--arrival-id` and `--outbound-date` (YYYY-MM-DD); add `--return-date` for a round trip, leave it out for one-way. Prices depend on the dates you pass, so run the same route on other dates to compare. `--currency` sets the currency (default USD), `--country` and `--lang` the Google locale. Durations, stops and emissions also come back as numbers: `duration_minutes`, `stops_count`, `emissions_kg`.

## Sample output

A real row from `google-flights-scraper search JFK --arrival-id LAX --outbound-date 2026-12-01 --return-date 2026-12-04 --currency USD --max-results 3` (2026-10-23):

```json
{
  "rank": 1,
  "price": "$397",
  "stops": "Nonstop",
  "airline": "JetBlue",
  "currency": "USD",
  "duration": "6 hr 22 min",
  "emissions": "426 kg CO2e",
  "trip_type": "round_trip",
  "arrival_id": "LAX",
  "price_value": 397,
  "return_date": "2026-12-04",
  "stops_count": 0,
  "arrival_time": "12:57 AM",
  "departure_id": "JFK",
  "emissions_kg": 426,
  "outbound_date": "2026-12-01",
  "departure_time": "9:35 PM",
  "arrival_airport": "Los Angeles International Airport",
  "duration_minutes": 382,
  "departure_airport": "John F. Kennedy International Airport"
}
```

## Python

```python
from quanticdata_google_flights_scraper import GoogleFlightsScraper

flights = GoogleFlightsScraper()  # saved login, or QUANTICDATA_API_KEY

trips = flights.search("JFK", arrival_id="LAX", outbound_date="2026-12-01", return_date="2026-12-04",
                       currency="USD", max_results=30)
for f in trips:
    print(f["price_value"], f["airline"], f["departure_time"], f["arrival_time"], f["stops"], f["emissions_kg"])
trips.to_csv("jfk_lax.csv")

nonstop = [f["price_value"] for f in trips if f["stops_count"] == 0 and f["price_value"]]
print("cheapest nonstop:", min(nonstop) if nonstop else None)
```

Each call returns a `Run`: iterate it for the rows (plain dicts), take `len()`, or save it with `to_csv()`, `to_json()`, `to_jsonl()` or `to_dataframe()` (pandas). Errors are specific: `InsufficientCredit`, `RateLimited`, `InvalidInput`, `JobFailed`, `AuthError`.

## Examples

- **Cheapest day to fly**: Price one route over a run of outbound dates, one-way or with a fixed trip length, and get the cheapest fare and the cheapest nonstop of each day. See [`examples/fare_calendar.py`](examples/fare_calendar.py).
- **Several routes in one CSV**: Run a list of routes such as JFK-LAX and MXP-LHR for the same dates and keep every itinerary with its route, airline, times and price. See [`examples/routes_to_csv.py`](examples/routes_to_csv.py).
- **Fare tracking**: Check the cheapest fare and the cheapest nonstop of a trip every day and keep the history in a CSV, to buy when the price drops. See [`examples/fare_watch.py`](examples/fare_watch.py).

## Command line

Results print as a table; `-o file.csv`, `-o file.json` or `-o file.jsonl` writes a file. List inputs take `a b c`, `a,b,c`, `@file.txt` (one per line) or `-` (stdin). `--no-wait` starts a long run in the background and prints its id; `google-flights-scraper run <id> -o out.csv` collects it later.

### `google-flights-scraper search`

Flight itineraries between two airports — airline, times, stops, price, emissions.

```
google-flights-scraper search DEPARTURE_ID [options]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `DEPARTURE_ID` | string |  | Departure airport or city IATA code, e.g. JFK. |
| `--arrival-id` | string |  | Arrival airport or city IATA code, e.g. LAX. Required. |
| `--outbound-date` | string |  | Departure date YYYY-MM-DD. Required. |
| `--return-date` | string |  | Return date YYYY-MM-DD — omit for one-way. |
| `--currency` | string |  | 3-letter price currency (USD, EUR…). Default USD. |
| `--country` | string |  | Country to run the request from, as an ISO 3166-1 alpha-2 code (us, gb, de...). |
| `--lang` | string |  | Interface language, e.g. en, it, de. |
| `--max-results` | integer | `15` | How many itineraries to deliver at most (1–30). You pay only for delivered itineraries. |

## Output fields

<details><summary><code>google-flights-scraper search</code>: 20 fields</summary>

| Field | Type | Description |
|---|---|---|
| `rank` | integer | 1-based position. |
| `airline` | string or null | Operating airline(s). |
| `departure_time` | string or null | Departure time as shown. |
| `arrival_time` | string or null | Arrival time as shown. |
| `duration` | string or null | Total duration ("5 hr 53 min"). |
| `stops` | string or null | "Nonstop", "1 stop"… |
| `price` | string or null | Price as shown. |
| `price_value` | number or null | Parsed numeric price. |
| `currency` | string or null | ISO currency code of the price. |
| `departure_airport` | string or null | Departure airport as shown. |
| `arrival_airport` | string or null | Arrival airport as shown. |
| `emissions` | string or null | CO2 estimate as shown. |
| `outbound_date` | string | Requested outbound date. |
| `return_date` | string or null | Requested return date (null = one-way). |
| `departure_id` | string | Departure IATA code as requested. |
| `arrival_id` | string | Arrival IATA code as requested. |
| `duration_minutes` | integer or null | Total duration in minutes. |
| `stops_count` | integer or null | Number of stops (0 = nonstop). |
| `emissions_kg` | number or null | CO2 estimate in kg. |
| `trip_type` | string | one_way or round_trip. |

</details>

## Sign-in and API keys

- `google-flights-scraper login` signs you in with OAuth 2.1 and PKCE in the browser. The token is stored in `~/.config/quanticdata/credentials.json` (readable only by you) and refreshed automatically. One login serves every QuanticData tool on the machine.
- No browser on the machine (SSH, Docker, Colab): run `google-flights-scraper login --no-browser`, open the link anywhere, then paste back the address the browser ends on.
- Scripts and CI: set `QUANTICDATA_API_KEY` to a key from the dashboard, or store one with `google-flights-scraper login --api-key`.
- `google-flights-scraper logout` revokes the token. The connection is listed under API keys in the dashboard as "API · QuanticData CLI"; deleting that key disconnects every machine that uses it.

## Pricing

The code is free and MIT-licensed. Runs are billed to your QuanticData account per delivered row, at the price shown on each collector page linked above; $2 of usage is free every month and failed runs are never billed. Plans with higher limits: [pricing](https://quanticdata.io/pricing/?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper).

## Other ways to call it

The same data over plain HTTP:

```bash
curl -X POST https://api.quanticdata.io/v1/scraper/collectors/google_flights/run \
  -H "Authorization: Bearer $QUANTICDATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"departure_id": "JFK", "arrival_id": "LAX", "outbound_date": "2026-12-01", "return_date": "2026-12-04", "currency": "USD", "max_results": 3}}'
```

- [API reference](https://quanticdata.io/docs/?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper) with Python, Node, PHP and curl examples.
- [MCP server](https://quanticdata.io/mcp-server/?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper) to give Claude, Cursor or any MCP client the same tools.
- [n8n node](https://github.com/quantumproxies/n8n-nodes-quanticdata) for no-code workflows.

## FAQ

**Is this Google Flights scraper free?**

The code is free and MIT-licensed. Scraping runs on your QuanticData account: $2 of usage is free every month with no card, then you pay per delivered row at the price shown on each collector page. Failed runs are never billed.

**Do I need proxies or a headless browser?**

No. You send two airport codes and your dates and get rows back; the requests run on QuanticData's side.

**Does it do one-way and round trips?**

Yes. Leave out --return-date for one-way; with it, the itineraries are priced as a round trip and trip_type says round_trip. Prices are for the dates you pass.

**How many itineraries can one run return?**

Up to 30 itineraries per run; ask for fewer with --max-results and you pay only for what is delivered.

**Can I export to CSV or Excel?**

Add -o flights.csv (or .json, .jsonl). Every field is a plain value, so the CSV opens cleanly in Excel or Google Sheets.

**Can I run it on a schedule?**

Yes. Set QUANTICDATA_API_KEY in the environment and call the CLI or examples/fare_watch.py from cron, GitHub Actions or any scheduler.

## Related scrapers

- [Google Hotels Scraper](https://github.com/quantumproxies/google-hotels-scraper): Google Hotels scraper for Python and the command line.
- [Booking.com Scraper](https://github.com/quantumproxies/booking-scraper): Booking scraper for Python and the command line.
- [Airbnb Scraper](https://github.com/quantumproxies/airbnb-scraper): Airbnb scraper for Python and the command line.

## License

MIT. Built and maintained by [QuanticData](https://quanticdata.io/?utm_source=github&utm_medium=readme&utm_campaign=google-flights-scraper).
