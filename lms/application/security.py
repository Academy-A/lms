from dataclasses import dataclass, field
from os import environ


@dataclass(frozen=True, slots=True, kw_only=True)
class SecurityConfig:
    secret_key: str = field(default_factory=lambda: environ["API_SECRET_KEY"])
