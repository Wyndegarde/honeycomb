from __future__ import annotations

from enum import Enum

POSTGRES_IMAGE = "postgres:18-alpine"
POSTGRES_PORT = 5432


class AppEnv(Enum):
    DEV = "dev"
    TEST = "test"

    @classmethod
    def from_str(cls, value: str) -> AppEnv:
        """Create enum from string, case-insensitive."""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"Unknown App environment: {value}")

    def __str__(self) -> str:
        return self.value
