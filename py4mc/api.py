import hashlib

from typing import Union
from collections.abc import Iterable

from .exceptions import ApiException, InvalidMetric
from .utils.checks import is_valid_uuid, is_valid_name
from .dispatcher import Dispatch
from .types.profile import Profile
from .types.misc import Statistics


class MojangApi:
    def __init__(self, asynchronous: bool = False, jwt_token: str = None):
        self.is_asynchronous = asynchronous
        self.dispatcher = Dispatch(jwt_token)

    def _get_profile_information(self, uuid: str):
        route = self.dispatcher.SESSION_SERVER + f"/session/minecraft/profile/{uuid}"
        profile = self.dispatcher.do_request("GET", route + "?unsigned=false")
        if not isinstance(profile, dict):
            return None
        properties = profile.get("properties")[0]
        return Profile(properties.get("value"), properties.get("signature"))

    def _chunk_profiles(self, profiles, chunk_size: int = 10):
        for iteration in range(0, len(profiles), chunk_size):
            yield profiles[iteration: iteration + chunk_size]

    def _get_uuids(self, profiles: Iterable):
        processed_uuids = []
        chunked_profiles = list(self._chunk_profiles(profiles))
        route = self.dispatcher.API_BASE + "/profiles/minecraft"
        for profile_chunk in chunked_profiles:
            chunk = list(filter(lambda n: is_valid_name(n), profile_chunk))
            response = self.dispatcher.do_request("POST", route, json=chunk)
            processed_uuids.extend([r.get("id") for r in response])
        return processed_uuids

    def get_user(self, profiles: Iterable):  # Code seems ugly but works so... No touch.
        retrieved_profiles = []
        if isinstance(profiles, str):
            route = self.dispatcher.API_BASE + f"/users/profiles/minecraft/{profiles}"
            response = self.dispatcher.do_request("GET", route)
            if not isinstance(response, dict):
                return None
            return self._get_profile_information(response.get("id"))
        profile_uuids = self._get_uuids(profiles)
        profile_uuids.extend(list(filter(lambda x: is_valid_uuid(x), profiles)))
        for profile_uuid in profile_uuids:
            profile_data = self._get_profile_information(profile_uuid)
            if profile_data is not None:
                retrieved_profiles.append(profile_data)
            else:
                continue
        return retrieved_profiles

    def get_blocked_servers(self, raw_hashes: bool = True):
        blocked_servers = []
        route = self.dispatcher.SESSION_SERVER + "/blockedservers"
        response = self.dispatcher.do_request("GET", route)
        for blocked_hash in response.content.splitlines():
            if not raw_hashes:
                server_hash = hashlib.sha1(blocked_hash)
                blocked_servers.append(server_hash)
            else:
                blocked_servers.append(blocked_hash.decode())
        return blocked_servers

    def get_statistics(self, metrics: Iterable):
        if len(metrics) == 0:
            raise ApiException("You must provide at least one metric!")
        for metric in metrics:
            if metric not in Statistics.VALID_METRICS:
                raise InvalidMetric(f"{metric} is not a valid metric!")
        route = Dispatch.API_BASE + "/orders/statistics"
        payload = {"metricKeys": metrics}
        statistics = self.dispatcher.do_request("POST", route, json = payload)
        return Statistics(statistics)

    def get_profile(self, profiles: Iterable):
        return self.get_user(profiles)
