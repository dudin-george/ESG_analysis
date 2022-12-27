import json
from datetime import datetime

from common.settings import Settings

settings = Settings()


def api_source() -> tuple[str, dict]:
    return f"{settings.api_url}/source/", {
        "id": 0,
        "site": "string",
        "source_type_id": 0,
        "parser_state": json.dumps({"bank_id": 100, "page": 1}),
        "last_update": str(datetime(2022, 1, 1)),
    }


def api_get_source_by_id() -> tuple[str, dict]:
    url, data = api_source()
    return url + f"item/{data['id']}", data


def api_bank() -> tuple[str, dict]:
    return f"{settings.api_url}/bank/", {
        "items": [
            {"id": 1, "bank_name": "string", "licence": "1", "description": "string"},
            {"id": 1000, "bank_name": "string", "licence": "1000", "description": "string"},
            {"id": 1234, "bank_name": "string", "licence": "1234", "description": "string"},
        ]
    }
