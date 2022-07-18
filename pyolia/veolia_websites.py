from __future__ import annotations

from enum import Enum, unique


@unique
class VeoliaWebsite(str, Enum):
    EAU_SERVICES = "www.eau-services.com"
    EAU_DU_GRAND_LYON = "agence.eaudugrandlyon.com"
