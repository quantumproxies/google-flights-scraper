"""Row types of each command, for editors and type checkers (rows are plain dicts)."""

from typing import Any, Dict, List, Optional

try:  # Python 3.8+
    from typing import TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict  # type: ignore


class GoogleFlightsRow(TypedDict, total=False):
    """One row of `google-flights-scraper search` (google_flights v1.1.0)."""

    rank: int
    """1-based position."""
    airline: Optional[str]
    """Operating airline(s)."""
    departure_time: Optional[str]
    """Departure time as shown."""
    arrival_time: Optional[str]
    """Arrival time as shown."""
    duration: Optional[str]
    """Total duration ("5 hr 53 min")."""
    stops: Optional[str]
    """"Nonstop", "1 stop"…"""
    price: Optional[str]
    """Price as shown."""
    price_value: Optional[float]
    """Parsed numeric price."""
    currency: Optional[str]
    """ISO currency code of the price."""
    departure_airport: Optional[str]
    """Departure airport as shown."""
    arrival_airport: Optional[str]
    """Arrival airport as shown."""
    emissions: Optional[str]
    """CO2 estimate as shown."""
    outbound_date: str
    """Requested outbound date."""
    return_date: Optional[str]
    """Requested return date (null = one-way)."""
    departure_id: str
    """Departure IATA code as requested."""
    arrival_id: str
    """Arrival IATA code as requested."""
    duration_minutes: Optional[int]
    """Total duration in minutes."""
    stops_count: Optional[int]
    """Number of stops (0 = nonstop)."""
    emissions_kg: Optional[float]
    """CO2 estimate in kg."""
    trip_type: str
    """one_way or round_trip."""
