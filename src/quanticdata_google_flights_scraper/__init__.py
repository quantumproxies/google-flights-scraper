"""Google Flights Scraper: Google Flights scraper for Python and the command line: one-way and round-trip itineraries between two airports for your dates, with airline, departure and arrival times, duration, stops, price and CO2 estimate, as JSON or CSV. Free and open source; sign in with your QuanticData account, no proxies or headless browser to run.

    from quanticdata_google_flights_scraper import GoogleFlightsScraper

    scraper = GoogleFlightsScraper()   # saved login (`google-flights-scraper login`) or QUANTICDATA_API_KEY
    run = scraper.search(...)   # Google Flights itineraries between two airports
"""

from typing import Any, Dict, Optional, Sequence, Union

from ._qd.client import Client, Run
from ._qd.errors import (APIError, AuthError, InsufficientCredit, InvalidInput, JobFailed, JobTimeout,
                         QuanticDataError, RateLimited)
from ._qd.output import write

__version__ = "0.1.0"
__all__ = ["GoogleFlightsScraper", "Run", "write", "APIError", "AuthError", "InsufficientCredit", "InvalidInput",
           "JobFailed", "JobTimeout", "QuanticDataError", "RateLimited", "__version__"]


def _as_list(value: Any) -> Any:
    if value is None or isinstance(value, (list, tuple)):
        return list(value) if value is not None else None
    return [value]


class GoogleFlightsScraper:
    """Google Flights Scraper on the QuanticData Data API.

    Every method runs one collector and returns a :class:`Run`: iterate it for the
    rows (plain dicts, typed in ``types``), or save it with ``to_csv()``,
    ``to_json()``, ``to_jsonl()`` or ``to_dataframe()``.
    """

    def __init__(self, api_key: Optional[str] = None, *, timeout: float = 180.0) -> None:
        self.client = Client(api_key, user_agent="google-flights-scraper/0.1.0 (+https://github.com/quantumproxies/google-flights-scraper)", timeout=timeout)

    def search(
        self, departure_id: str,
        *,
        arrival_id: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        currency: Optional[str] = None,
        country: Optional[str] = None,
        lang: Optional[str] = None,
        max_results: Optional[int] = None,
        wait: bool = True,
        timeout: float = 900.0,
    ) -> Run:
        """Flight itineraries between two airports — airline, times, stops, price, emissions.

        Args:
            departure_id: Departure airport or city IATA code, e.g. JFK.
            arrival_id: Arrival airport or city IATA code, e.g. LAX.
            outbound_date: Departure date YYYY-MM-DD.
            return_date: Return date YYYY-MM-DD — omit for one-way.
            currency: 3-letter price currency (USD, EUR…). Default USD.
            country: Country to run the request from, as an ISO 3166-1 alpha-2 code (us, gb, de...).
            lang: Interface language, e.g. en, it, de.
            max_results: How many itineraries to deliver at most (1–30). You pay only for delivered itineraries.
            wait: False starts the run in the background and returns its id at once.
            timeout: seconds to wait for a background run before giving up.

        Returns up to 30 rows, one per itinerary: see ``types.GoogleFlightsRow``.
        """
        payload = {
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "currency": currency,
            "country": country,
            "lang": lang,
            "max_results": max_results,
        }
        return self.client.run_collector("google_flights", payload, wait=wait, timeout=timeout)
