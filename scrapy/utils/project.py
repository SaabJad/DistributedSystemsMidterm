"""Project settings shim used by the minimal scrapy implementation.

Returns a plain dict of settings. Real Scrapy offers a complex Settings object
— this shim returns a lightweight mapping that is sufficient for the small
crawler used in this project.
"""
from typing import Dict


def get_project_settings() -> Dict:
    # Minimal settings placeholder. Add keys here if your spiders expect them.
    return {
        "USER_AGENT": "scrapy-shim/0.1",
    }


__all__ = ["get_project_settings"]
