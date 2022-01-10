import base64
import json

from uuid import UUID
from functools import reduce
from datetime import datetime

from ..dispatcher import Dispatch
from .textures import Skin, Cape


class Profile:
    def __init__(self, profile_value: str, signature: str):
        profile = self._process_value(profile_value)
        self.uuid = UUID(profile.get("profileId"), version = 4)
        self.username = profile.get("profileName")
        timestamp = int(profile.get("timestamp")) // 1000
        self.timestamp = datetime.utcfromtimestamp(timestamp)
        self.skin, self.cape = self._parse_textures(profile)
        self.default_skin = self._get_default_skin(self.uuid)
        self.signature = signature

    def __str__(self):
        return self.username

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<Profile {}>".format(" ".join(arguments))

    def _process_value(self, profile_value: str):
        decoded_value = base64.b64decode(profile_value)
        processed_value = json.loads(decoded_value)
        return processed_value

    def _get_default_skin(self, uuid: UUID):
        uuid_values = list()
        for number in [7, 15, 23, 31]:
            converted_uuid = int(uuid.hex[number], 16)
            uuid_values.append(converted_uuid)
        hash_code = reduce(lambda x, y: x ^ y, uuid_values)
        if hash_code % 2 == 0:
            return "Steve"
        return "Alex"

    def _parse_textures(self, profile: str):
        textures = profile.get("textures")
        skin = textures.get("SKIN")
        if skin.get("metadata") is not None:
            model_type = "slim"
        else:
            model_type = "classic"
        if textures.get("CAPE") is not None:
            cape_url = textures.get("CAPE").get("url")
            return Skin(skin.get("url"), model_type), Cape(cape_url)
        return Skin(skin.get("url"), model_type), None

    def name_history(self):
        route = Dispatch.API_BASE + "/user/profiles/{}/names".format(self.uuid)
        previous_names = Dispatch.do_request("GET", route)
        if len(previous_names) == 1:
            return HistoryIndex(previous_names[0])
        return [HistoryIndex(v) for v in previous_names]


class HistoryIndex:
    def __init__(self, raw_data: dict):
        self.name = raw_data.get("name")
        self.changed_at = raw_data.get("changedToAt")
        if self.changed_at is None:
            self.is_original = True
        else:
            timestamp = int(self.changed_at) // 1000
            self.changed_at = datetime.utcfromtimestamp(timestamp)
            self.is_original = False

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<HistoryIndex {}>".format(" ".join(arguments))
