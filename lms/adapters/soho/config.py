from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, kw_only=True, slots=True)
class SohoConfig:
    token: str = field(default_factory=lambda: environ["APP_SOHO_API_TOKEN"])
