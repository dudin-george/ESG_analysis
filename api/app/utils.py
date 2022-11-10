from typing import Any

import aiohttp


async def get_json_request(url: str, headers: dict[str, str] | None = None) -> dict[str, Any] | None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()  # type: ignore
            return None
