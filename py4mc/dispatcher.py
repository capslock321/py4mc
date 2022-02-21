import requests

from typing import Union
from requests import Response

from .utils.checks import is_valid_json
from .exceptions import InternalServerException, ApiException


class Dispatch:
    API_BASE = "https://api.mojang.com"
    SESSION_SERVER = "https://sessionserver.mojang.com"
    SERVICE_URL = "https://api.minecraftservices.com"

    @classmethod
    def do_request(cls, method: str, route: str, **kwargs):
        if kwargs.get("headers") is None:
            kwargs["headers"] = {"Content-Type": "application/json"}
        elif kwargs["headers"].get("Content-Type") is None:
            kwargs["headers"].update({"Content-Type": "application/json"})
        response = requests.request(method, route, **kwargs)
        return cls.parse_response(response)

    @staticmethod
    def _find_problems(response: dict) -> bool:
        if response.get("error") is not None:
            exception_format = (
                f"{response.get('error')}: {response.get('errorMessage')}"
            )
            raise ApiException(
                f"An exception has occurred while trying to parse the response: {exception_format}"
            )
        return False

    @classmethod
    def parse_response(cls, response: Response) -> Union[bool, dict, list]:
        if response.status_code == 200:
            if is_valid_json(response.text):
                if isinstance(response.json(), list):
                    return response.json()
                elif not cls._find_problems(response.json()):
                    return response.json()
            else:
                return response
        elif response.status_code >= 500:
            raise InternalServerException(
                "A status code greater than 500 was received."
            )
        return response  # If we don't understand the response returned.
