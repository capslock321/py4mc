from requests import Response
from typing import Union

from ..utils.checks import is_valid_json
from ..exceptions import InternalServerException, ApiException


class MojangApiResponse:
    def __init__(self, response: Response):
        self.raw_response = response
        self.is_empty = bool(response.content)

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<MojangApiResponse {}>".format(" ".join(arguments))

    def _find_problems(self, response: dict) -> bool:
        if response.get("error") is not None:
            exception_format = f"{response.get('error')}: {response.get('errorMessage')}"
            raise ApiException(f"An exception has occurred while trying to parse the response: {exception_format}")
        return False

    def parse_response(self) -> Union[bool, dict, list]:
        if self.raw_response.status_code == 200:
            if is_valid_json(self.raw_response.text):
                if isinstance(self.raw_response.json(), list):
                    return self.raw_response.json()
                elif not self._find_problems(self.raw_response.json()):
                    return self.raw_response.json()
            else:
                return self.raw_response.text
        elif self.raw_response.status_code >= 500:
            raise InternalServerException(
                "A status code greater than 500 was received."
            )
        return self.raw_response  # If we don't understand the response returned.
