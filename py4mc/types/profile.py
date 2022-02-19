import base64
import json

from uuid import UUID
from typing import Union
from functools import reduce
from datetime import datetime

from ..dispatcher import Dispatch
from .textures import Skin, Cape


class Profile:
    """Represents a profile from the Mojang API.

    A profile is not a logged in account! You cannot preform any actions that
    require authentication with this class!

    Notes:
        When making the profile information request, we always set unsigned to false.
        This is because setting unsigned to true or not at all does not seem to change anything.
        The signature is another potentially useful piece of information a user can use.

    Attributes:
        profile (dict): The raw profile dictionary.
        uuid (UUID): The profile's uuid.
        username (str): The profile's current username.
        timestamp (datetime): The time the server processed your request.
        signature (str): The request signature.

    """
    def __init__(self, profile_value: str, signature: str):
        self.profile = self._process_value(profile_value)
        self.uuid = UUID(self.profile.get("profileId"), version=4)
        self.username = self.profile.get("profileName")
        self.timestamp = self.get_timestamp()
        self.signature = signature

    def __str__(self):
        return self.username

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<Profile {}>".format(" ".join(arguments))

    def get_timestamp(self) -> datetime:
        """Gets the timestamp of the request.

        When you make a request, a timestamp is returned.
        The timestamp represents the time the server received your request.

        Returns:
            datetime: The datetime object to the timestamp.
        """
        timestamp = int(self.profile.get("timestamp")) // 1000
        return datetime.utcfromtimestamp(timestamp)

    def _process_value(self, profile_value: str) -> dict:
        """Decodes the Base64 profile data returned.

        Args:
            profile_value: The base64 object.

        Returns:
            dict: The processed base64 value.
        """
        decoded_value = base64.b64decode(profile_value)
        processed_value = json.loads(decoded_value)
        return processed_value

    def default_skin(self) -> str:
        """Get the profiles default skin.

        This gets the Java hashcode of the profile's uuid.
        If the hashcode is even, the default skin is a Steve.
        Otherwise, the skin is an Alex.

        Returns:
            str: Steve if the profile's default skin is Steve, Alex if it's Alex.
        """
        uuid_values = list()
        for number in [7, 15, 23, 31]:
            converted_uuid = int(self.uuid.hex[number], 16)
            uuid_values.append(converted_uuid)
        hash_code = reduce(lambda x, y: x ^ y, uuid_values)
        if hash_code % 2 == 0:
            return "Steve"
        return "Alex"

    def get_skin(self) -> Skin:
        """Gets the profile's skin.

        If there is a metadata, then the skin is in the slim style.
        Else it is in the classic style.

        Returns:
            Skin: The profile's skin.
        """
        textures = self.profile.get("textures")
        skin = textures.get("SKIN")
        if skin.get("metadata") is not None:
            model_type = "slim"
        else:
            model_type = "classic"
        return Skin(skin.get("url"), model_type)

    def get_cape(self) -> Union[bool, Cape]:
        """Gets the profile's cape.

        Returns:
            Cape: The profile's cape.
            bool: Returns None if the profile does not have a cape.
        """
        textures = self.profile.get("textures")
        if textures.get("CAPE") is None:
            return None
        return Cape(textures.get("CAPE"))

    def name_history(self) -> list:
        """Gets the profile's name history.

        If there is only one name in the name history, then it
        will return a HistoryIndex object. If not, it returns a
        list of HistoryIndex objects.

        Returns:
            HistoryIndex: One of the profile's names.
            list: A list of the profile's old names.

        """
        route = Dispatch.API_BASE + "/user/profiles/{}/names".format(self.uuid)
        previous_names = Dispatch.do_request("GET", route)
        if len(previous_names) == 1:
            return HistoryIndex(previous_names[0])
        return [HistoryIndex(v) for v in previous_names]


class HistoryIndex:
    """Represents one element of a profile's history of names.

    Attributes:
        raw_data (dict): The profile's raw name data.
        name (str): One of the profile's old names.
        changed_at (datetime): The time they changed the name. Can be None if they have never done so.
        is_original (bool): If the name is their original name. Is True if it is their original name.

    """
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
