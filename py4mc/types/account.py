import py4mc

from ..dispatcher import Dispatch
from .profile import Profile
from .misc import AccountAttributes
from ..exceptions import AuthenticationException

class Account:

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._auth = {"Authorization": f"Bearer {access_token}"}
        self.account = self._account_information()
        self.mojang = py4mc.MojangApi()

    def get_profile(self) -> Profile:
        profile_uuid = self.account.get("id")
        return self.mojang.get_profile(profile_uuid)

    def auth_request(self, method: str, route: str):
        response = Dispatch.do_request(method, route, headers = self._auth)
        if not isinstance(response, dict):
            raise AuthenticationException("Invalid access token was passed.")
        return response

    def _account_information(self):
        route = f"{Dispatch.SERVICE_URL}/minecraft/profile"
        return self.auth_request("GET", route)

    def get_attributes(self):
        route = f"{Dispatch.SERVICE_URL}/player/attributes"
        response = self.auth_request("GET", route)
        return AccountAttributes(response)
