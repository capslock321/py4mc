import base64
import json

from uuid import UUID
from functools import reduce
from datetime import datetime

from ..dispatcher import Dispatch
from .textures import Skin, Cape


class Profile:
    def __init__(self, profile_value: str, signature: str):
        self.profile = self._process_value(profile_value)
        self.uuid = UUID(self.profile.get("profileId"), version=4)
        self.username = self.profile.get("profileName")
        self.timestamp = self.get_timestamp(self.profile)
        self.signature = signature

    def __str__(self):
        return self.username

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<Profile {}>".format(" ".join(arguments))

    def get_timestamp(self, profile):
        timestamp = int(profile.get("timestamp")) // 1000
        return datetime.utcfromtimestamp(timestamp)

    def _process_value(self, profile_value: str):
        decoded_value = base64.b64decode(profile_value)
        processed_value = json.loads(decoded_value)
        return processed_value

    def default_skin(self) -> str:
        uuid_values = list()
        for number in [7, 15, 23, 31]:
            converted_uuid = int(self.uuid.hex[number], 16)
            uuid_values.append(converted_uuid)
        hash_code = reduce(lambda x, y: x ^ y, uuid_values)
        if hash_code % 2 == 0:
            return "Steve"
        return "Alex"

    def get_skin(self) -> Skin:
        textures = self.profile.get("textures")
        skin = textures.get("SKIN")
        if skin.get("metadata") is not None:
            model_type = "slim"
        else:
            model_type = "classic"
        return Skin(skin.get("url"), model_type)

    def get_cape(self):
        textures = self.profile.get("textures")
        if textures.get("CAPE") is None:
            return None
        return Cape(textures.get("CAPE"))

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
