""" Python wrapper for the Veolia unofficial API """
from __future__ import annotations

from datetime import date
from types import TracebackType
from typing import Any

import backoff
from aiohttp import ClientSession

from pyolia.clients.eau_services_client import EauServicesClient
from pyolia.exceptions import NotAuthenticatedException, BadCredentialsException
from pyolia.veolia_websites import VeoliaWebsite


async def relogin(invocation: dict[str, Any]) -> None:
    await invocation["args"][0].login()


class VeoliaClient:
    """Interface class for the Veolia unofficial API"""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession = None,
        website: VeoliaWebsite = VeoliaWebsite.EAU_DU_GRAND_LYON,
    ) -> None:
        """
        Constructor

        :param username: the username used to log in
        :param password: the password used to log in
        :param website: the website to use. Default to eau-services.
        :param session: optional ClientSession
        """

        self.username = username
        self.password = password
        self.session = session if session else ClientSession()

        if website in [VeoliaWebsite.EAU_SERVICES, VeoliaWebsite.EAU_DU_GRAND_LYON]:
            self.client = EauServicesClient(self.session, website)

    async def __aenter__(self) -> VeoliaClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session."""
        await self.session.close()

    @property
    def last_report_date(self) -> date:
        """Date since which reports have been published."""
        return self.client.last_report_date

    @backoff.on_exception(
        backoff.expo,
        NotAuthenticatedException,
        max_tries=2,
        on_backoff=relogin,
    )
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
        return await self.client.get_consumption(month, year, day)

    async def login(self) -> None:
        """Log into the Veolia website."""
        await self.client.login(self.username, self.password)
