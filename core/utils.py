import aiohttp
import json


class BaseUtils:

    @staticmethod
    async def make_get_request(url, headers):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            response = await session.get(url=url)
            if response.status == 200:
                return json.loads(await response.text())
