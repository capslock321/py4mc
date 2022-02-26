import urllib
import webbrowser

from .dispatcher import Dispatch
from .exceptions import AuthenticationException


class MicrosoftOAuth:  # Add refresh token
    AUTH_TOKEN_URL = "https://login.live.com/oauth20_token.srf"

    AUTH_CODE_URL = "https://login.live.com/oauth20_authorize.srf"

    def __init__(self, client_id: str, redirect_uri: str = "https://localhost"):
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def build_url(self, state: str = None, open_webbrowser: bool = False) -> str:
        url_query_arguments = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "XboxLive.signin offline_access",
        }
        if state is not None:
            url_query_arguments["state"] = state
        arguments = urllib.parse.urlencode(url_query_arguments)
        oauth_code_url = f"{self.AUTH_CODE_URL}?{arguments}"
        if open_webbrowser:
            webbrowser.open(oauth_code_url)
        return oauth_code_url

    def get_oauth_token(self, code: str):
        payload_arguments = {
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = Dispatch.do_request(
            "POST", self.AUTH_TOKEN_URL, data=payload_arguments, headers=headers
        )
        if not isinstance(response, dict):
            raise AuthenticationException(response.json().get("error_description"))
        return response.get("access_token")


class MinecraftAuthentication:
    XBL_URL = "https://user.auth.xboxlive.com/user/authenticate"

    XSTS_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"

    MINECRAFT_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"

    @classmethod
    def get_xbl_token(cls, access_token: str):
        payload_arguments = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d={}".format(access_token),
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }
        response = Dispatch.do_request("POST", cls.XBL_URL, json=payload_arguments)
        if not isinstance(response, dict):
            raise AuthenticationException("Invalid Access Token was provided.")
        return response.get("Token")

    @classmethod
    def get_xsts_token(cls, user_token: str):
        payload_arguments = {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [user_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        }
        response = Dispatch.do_request("POST", cls.XSTS_URL, json=payload_arguments)
        if not isinstance(response, dict):
            raise AuthenticationException("Invalid User Token was provided.")
        if response.get("XErr") is not None:
            raise AuthenticationException(
                f"XSTS returned error code {response.get('XErr')}!"
            )
        return response.get("Token"), response["DisplayClaims"]["xui"][0]["uhs"]

    @classmethod
    def get_access_token(cls, xsts_token: str, uhs: int):
        payload = {"identityToken": f"XBL3.0 x={uhs};{xsts_token}"}
        response = Dispatch.do_request("POST", cls.MINECRAFT_URL, json=payload)
        if not isinstance(response, dict):
            raise AuthenticationException(response.json().get("error"))
        return response.get("access_token")
