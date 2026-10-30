"""`python -m quanticdata_google_flights_scraper` and the `google-flights-scraper` command."""

import os
import sys

from ._qd.cli import load_spec, main


def run() -> None:
    sys.exit(main(load_spec(os.path.dirname(os.path.abspath(__file__)))))


if __name__ == "__main__":
    run()
