import json

from string import ascii_letters
from uuid import UUID


def is_valid_uuid(uuid: UUID, version: int = 4):
    try:
        UUID(uuid, version=version)
        return True
    except ValueError:
        return False


def is_valid_json(string: str):
    try:
        json.loads(string)
        return True
    except Exception:
        return False


def is_valid_name(name: str):
    """Checks if the given string is a valid Minecraft username.

    Mojang does not complain with names under 3 chars long.
    25 characters is the limit before Mojang starts throwing errors.

    Args:
        name (str): The name to check.

    Returns:
        bool: True if name is valid, False if it is not.
    """
    if len(name) <= 25:
        return all(x in ascii_letters + "_" for x in name)
    return False
