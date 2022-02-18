import requests

from .utils.parsers import MojangApiResponse

class Dispatch:

    API_BASE = "https://api.mojang.com"
    SESSION_SERVER = "https://sessionserver.mojang.com"

    @classmethod
    def do_request(cls, method: str, route: str, **kwargs):
        if kwargs.get("headers") is None:
            kwargs["headers"] = {"Content-Type": "application/json"}
        else:
            kwargs["headers"].update({"Content-Type": "application/json"})
        response = requests.request(method, route, **kwargs)
        return MojangApiResponse(response).parse_response()
