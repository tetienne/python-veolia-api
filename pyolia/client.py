""" Python wrapper for the Veolia unofficial API """
from __future__ import annotations

import csv
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional, Type, Union

import backoff
from aiohttp import ClientSession

JSON = Union[Dict[str, Any], List[Dict[str, Any]]]

DOMAIN = "https://www.eau-services.com"
LOGIN_URL = f"{DOMAIN}/default.aspx"
DATA_URL = f"{DOMAIN}/mon-espace-suivi-personnalise.aspx?ex=1&mm={{}}/{{}}"


async def relogin(invocation: Dict[str, Any]) -> None:
    await invocation["args"][0].login()


class NotAuthenticatedException(Exception):
    pass


class BadCredentialsException(Exception):
    pass


class VeoliaClient:
    """ Interface class for the Veolia unofficial API """

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession = None,
    ) -> None:
        """
        Constructor

        :param username: the username for eau-services.com
        :param password: the password for eau-services.com
        :param session: optional ClientSession
        """

        self.username = username
        self.password = password
        self.session = session if session else ClientSession()

    async def __aenter__(self) -> VeoliaClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session."""
        await self.session.close()

    @backoff.on_exception(
        backoff.expo,
        NotAuthenticatedException,
        max_tries=2,
        on_backoff=relogin,
    )
    async def get_consumption(self, month: int, year: int) -> Dict[float, int]:
        """Return the water consumption for the given month and year in liter."""
        if month > 12 or month < 1:
            raise ValueError("month must be between 1 and 12 included.")
        if year < 2001:
            raise ValueError("year must be greater than 2000")

        async with self.session.get(DATA_URL.format(month, year)) as response:
            if response.url.name == "inscription.aspx":
                raise NotAuthenticatedException
            data = await response.text()

        reader = csv.reader(data.splitlines(), delimiter=";")
        next(reader)  # skip header line
        return {
            datetime.strptime(row[0], "%d/%m/%Y").timestamp(): int(row[1])
            for row in reader
        }

    async def login(self) -> None:
        """Log into the Veolia website."""
        async with await self.session.post(
            LOGIN_URL, data={"login": self.username, "pass": self.password}
        ) as response:
            if response.url.name == "connexion.aspx":
                raise BadCredentialsException
