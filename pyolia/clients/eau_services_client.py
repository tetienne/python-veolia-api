from __future__ import annotations

import csv
from datetime import date, datetime, timedelta

from aiohttp import ClientSession

from pyolia.exceptions import BadCredentialsException, NotAuthenticatedException
from pyolia.veolia_websites import VeoliaWebsite

DOMAIN = "https://www.eau-services.com"
LOGIN_URL = f"{DOMAIN}/default.aspx"
DATA_URL = f"{DOMAIN}/mon-espace-suivi-personnalise.aspx?ex=1&mm={{}}/{{}}"
DATA_URL_DAY = f"{DATA_URL}&d={{}}"

CSV_DELIMITER = ";"
CONSUMPTION_HEADER = "consommation(litre)"


class EauServicesClient:
    def __init__(self, session: ClientSession, website: VeoliaWebsite) -> None:
        self.session = session
        self.url = website

    @property
    def last_report_date(self) -> date:
        """Date since which reports have been published."""
        return datetime.now().date() - timedelta(days=3)

    async def get_consumption(
        self, month: int, year: int, day: int = None
    ) -> list[int]:
        """
        If day is not provided, return the water consumption in liter for each hour for
        the given day. The first item matches 1h, the last one 24h.
        Else return the return the water consumption in liter for each day for the
        given month.
        The consumption is not available for the last 3 days.
        """
        if year < 2001:
            raise ValueError("year must be greater than 2000")

        if date(year, month, day if day else 1) > datetime.now().date():
            raise ValueError("Cannot retrieve consumption from the future.")

        if day:
            return await self._get_hourly_consumption(month, year, day)
        return await self._get_daily_consumption(month, year)

    async def _get_daily_consumption(self, month: int, year: int) -> list[int]:
        async with self.session.get(DATA_URL.format(month, year)) as response:
            if response.url.name != "mon-espace-suivi-personnalise.aspx":
                raise NotAuthenticatedException
            data = await response.text()

        reader = csv.DictReader(data.splitlines(), delimiter=CSV_DELIMITER)
        return [int(row[CONSUMPTION_HEADER]) for row in reader]

    async def _get_hourly_consumption(
        self, month: int, year: int, day: int
    ) -> list[int]:
        if date(year, month, day) > self.last_report_date:
            raise ValueError(
                f"Hourly consumption is only available for date "
                f"before {self.last_report_date}"
            )

        async with self.session.get(DATA_URL_DAY.format(month, year, day)) as response:
            if response.url.name == "inscription.aspx":
                raise NotAuthenticatedException
            data = await response.text()

        reader = csv.DictReader(data.splitlines(), delimiter=CSV_DELIMITER)
        try:
            return [int(row[CONSUMPTION_HEADER]) for row in reader]
        except IndexError:
            # Hourly consumption is not enabled
            return []

    async def login(self, username: str, password: str) -> None:
        """Log into the Veolia website."""
        async with await self.session.post(
            LOGIN_URL, data={"login": username, "pass": password}
        ) as response:
            if response.url.name == "connexion.aspx":
                raise BadCredentialsException
