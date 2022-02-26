# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2021 capslock321

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import requests

from typing import Union, Optional
from requests import Response
from collections.abc import Iterable

from .exceptions import ApiException, InvalidMetric, AuthenticationException
from .authentication import MicrosoftOAuth, MinecraftAuthentication
from .utils.checks import is_valid_uuid, is_valid_name
from .dispatcher import Dispatch

from .types.profile import Profile
from .types.account import Account
from .types.misc import Statistics


class MojangApi:
    """Everything regarding the Mojang API is within this class.

    Anything regarding Mojang's API that is documented in wiki.vg, has been implemented in some sort in this library.
    """

    def get_profile_attributes(self, uuid: str):
        """Retrieves the profile information given the users UUID.

        Instead of making multiple requests to retrieve the relevant profile attributes,
        we make only one request to get all of the relevant profile attributes.

        Args:
            uuid (UUID): The profile's UUID.

        Returns:
            Union[Profile, bool]: The profile retrieved, or None if the profile was not found.

        """
        route = Dispatch.SESSION_SERVER + f"/session/minecraft/profile/{uuid}"
        profile = Dispatch.do_request("GET", route + "?unsigned=false")
        if not isinstance(profile, dict):
            return None
        properties = profile.get("properties")[0]
        return Profile(properties.get("value"), properties.get("signature"))

    def _chunk_usernames(self, usernames, chunk_size: int = 10):
        """Splits the given profiles into multiple lists.

        This chunks a large list, into smaller lists so more than 10 names can be provided into the get_profile method.

        Args:
            usernames (Iterable): The large profile list to chunk.
            chunk_size (int): The size each chunked list.

        Yields:
            list: The chunked list.

        """
        for iteration in range(0, len(usernames), chunk_size):
            yield usernames[iteration : iteration + chunk_size]

    def get_uuid(self, username: str) -> Union[bool, str]:
        """Gets the uuid of the given username.

        Args:
            username: The username to get the uuid of.

        Returns:
            bool: Returns None if no person with that name is found.
            str: The uuid of the username given.

        """
        route = Dispatch.API_BASE + "/users/profiles/minecraft/"
        response = Dispatch.do_request("GET", route + username)
        if isinstance(response, Response):
            return None
        return response.get("id")

    def get_uuids(self, usernames: Iterable) -> str:
        """Attempts to get all UUIDS of the given profiles.

        Because the API can only take 10 names per request, we can chunk a list larger than 10 names so
        instead of having to discard any names past the first ten, we can return to the user all of
        their requested names, albeit a little slower.

        Args:
            usernames (Iterable): An iterable of names.

        Returns:
            list: The UUID's associated with each name.

        """
        processed_uuids = []
        chunked_profiles = list(self._chunk_usernames(usernames))
        route = Dispatch.API_BASE + "/profiles/minecraft"
        for profile_chunk in chunked_profiles:
            chunk = [c for c in profile_chunk if is_valid_name(c)]
            response = Dispatch.do_request("POST", route, json=chunk)
            processed_uuids.extend([r.get("id") for r in response])
        return processed_uuids

    def _postprocess_profiles(
        self, profiles: Union[str, Iterable]
    ) -> Union[Profile, list, bool]:
        """Processes the profiles before returning.

        If there are no profiles, then None is returned. However, if
        there is only one profile in the list, then we return the singular
        Profile object within that list. Else we just return the list.

        Args:
            profiles: The list of profiles to process.

        Returns:
            Profile: If there is only a singular profile in the list.
            list: If there are multiple profiles in the list.
            bool: If there are no elements in the list.

        """
        if not profiles:
            return None
        elif len(profiles) == 1:
            return profiles[0]
        return profiles

    def get_user(self, profiles: Union[str, Iterable]):
        """Gets the specified profiles attributes.

        The argument can be either a single string, or an iterable of strings.

        Notes:
            No user can have a valid Minecraft UUID as a username,
            therefore we exclude the uuids from getting checked to speed up the profile gathering process.

        Args:
            profiles (Union[str, Iterable]): The profiles to retrieve from the API.

        Returns:
            Union[Profile, list]: The retrieved profiles.
        """
        retrieved_profiles = []
        if isinstance(profiles, str):
            profiles = [
                profiles,
            ]
        for profile in profiles:
            if not is_valid_uuid(profile):
                profile = self.get_uuid(profile)
            profile_data = self.get_profile_attributes(profile)
            retrieved_profiles.append(profile_data)
        return self._postprocess_profiles(retrieved_profiles)

    def get_blocked_servers(self, raw_hashes: bool = True):
        """Retrieves a list of blocked servers.

        Upon connecting to a server, the client will check if the hashed server IP is within this list.
        If it is, then it will not connect to that server.

        Args:
            raw_hashes (bool): If the hashes should not be converted into a _hashlib.HASH object.

        Returns:
            list: A list of blocked hashes.
        """
        blocked_servers = []
        route = Dispatch.SESSION_SERVER + "/blockedservers"
        response = requests.request("GET", route)
        for blocked_hash in response.content.splitlines():
            if not raw_hashes:
                server_hash = hashlib.sha1(blocked_hash)
                blocked_servers.append(server_hash)
            else:
                blocked_servers.append(blocked_hash.decode())
        return blocked_servers

    def get_statistics(self, metrics: Iterable):
        """Gets Mojang sales statistics.

        Note:
            You can find a list of valid queries in Statistics.VALID_METRICS.

        Args:
            metrics (Iterable): A list of valid metrics to query.

        Returns:
            Statistics: The returned statistics.

        Raises:
            ApiException: If you do not provide any metrics.
            InvalidMetric: If you provided one or more invalid metrics.

        """
        if len(metrics) == 0:
            raise ApiException("You must provide at least one metric!")
        if isinstance(metrics, str):
            metrics = [
                metrics,
            ]
        for metric in metrics:
            if metric not in Statistics.VALID_METRICS:
                raise InvalidMetric(f"{metric} is not a valid metric!")
        route = Dispatch.API_BASE + "/orders/statistics"
        payload = {"metricKeys": metrics}
        statistics = Dispatch.do_request("POST", route, json=payload)
        return Statistics(statistics)

    def get_profile(self, profiles: Iterable):
        """An alias for get_user.

        Check the get_user method for extended documentation.
        """
        return self.get_user(profiles)

    def get_account(
        self,
        client_id: str,
        redirect_uri: Optional[str] = "https://localhost",
        state: Optional[str] = None,
        open_webbrowser: Optional[bool] = False,
        code: Optional[str] = None,
        access_token: Optional[str] = None
    ):  # Add automatic wgsi server to get code using http.server. Maybe find better way to get account?
        if access_token is not None:
            return Account(access_token)
        microsoft_oauth = MicrosoftOAuth(client_id, redirect_uri)
        if code is None:
            return microsoft_oauth.build_url(state, open_webbrowser)
        oauth_token = microsoft_oauth.get_oauth_token(code)
        xbl_token = MinecraftAuthentication.get_xbl_token(oauth_token)
        xsts_token, user_hash = MinecraftAuthentication.get_xsts_token(xbl_token)
        return Account(MinecraftAuthentication.get_access_token(xsts_token, user_hash))
