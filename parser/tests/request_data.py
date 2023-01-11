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
            {"id": 2761, "bank_name": "string", "licence": "2761", "description": "string"},
        ]
    }


def api_broker() -> tuple[str, dict]:
    return f"{settings.api_url}/bank/broker", {
        "items": [
            {"id": 1001, "bank_name": "string", "licence": "17712660100000", "description": "string"},
            {"id": 1002, "bank_name": "string", "licence": "04512685100000", "description": "string"},
            {"id": 1003, "bank_name": "string", "licence": "04502972100000", "description": "string"},
        ]
    }


def api_insurance() -> tuple[str, dict]:
    return f"{settings.api_url}/bank/insurance", {
        "items": [
            {"id": 1001, "bank_name": "string", "licence": "2496", "description": "string"},
            {"id": 1002, "bank_name": "string", "licence": "0796", "description": "string"},
            {"id": 1003, "bank_name": "string", "licence": "3947", "description": "string"},
        ]
    }


def api_mfo() -> tuple[str, dict]:
    return f"{settings.api_url}/bank/mfo", {
        "items": [
            {"id": 1001, "bank_name": "string", "licence": "651303532004088", "description": '{"ogrn":1134205019189}'},
            {"id": 1002, "bank_name": "string", "licence": "1903550009325", "description": '{"ogrn":1134205019189}'},
            {"id": 1003, "bank_name": "string", "licence": "1903475009492", "description": '{"ogrn":1134205019189}'},
        ]
    }
