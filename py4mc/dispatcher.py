import requests
import aiohttp

from .utils.checks import is_valid_json
from .exceptions import ApiException, InternalServerException


def parse_response(response: requests.Response):
    if response.status_code >= 500:
        raise InternalServerException("Something went wrong at Mojang's side.")
    if response.status_code == requests.codes.ok:
        if is_valid_json(response.content):
            response_json = response.json()
            if not isinstance(response_json, list) and response_json.get("error") is not None:
                error_format = f"{response_json.get('error')}: {response_json.get('errorMessage')}"
                raise ApiException(f"An exception occurred while trying to parse the response: {error_format}")
            return response_json
        else:
            return response
    return response


class Dispatch:

    API_BASE = "https://api.mojang.com"
    SESSION_SERVER = "https://sessionserver.mojang.com"

    def __init__(self, jwt_token: str = None):
        self.jwt_token = jwt_token
        if jwt_token is not None:
            self._auth = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json",
            }

    @classmethod
    def do_request(cls, method: str, route: str, **kwargs):
        response = requests.request(method, route, **kwargs)
        parsed_response = parse_response(response)
        return parsed_response

    async def do_asynchronous_request(self, method: str, route: str, **kwargs):
        session = await aiohttp.ClientSession()
        async with session.request(method, route, **kwargs) as response:
            try:
                parsed_response = self._parse_response(response)
            finally:
                await session.close()
        return parsed_response
