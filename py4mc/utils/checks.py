import json

from string import ascii_letters
from uuid import UUID


def is_valid_uuid(uuid: UUID, version: int = 4) -> bool:
    """Checks if the given uuid is valid.

    Args:
        uuid: The uuid to check.
        version: The uuid version to check.

    Returns:
        bool: True if the uuid is valid, False if it is not.
    """
    try:
        UUID(uuid, version=version)
        return True
    except ValueError:
        return False


def is_valid_json(string: str) -> bool:
    """Checks if the given string is valid json.

    Args:
        string: The string to check.

    Returns:
        bool: True if the string is valid json, False if it is not.
    """
    try:
        json.loads(string)
        return True
    except Exception:
        return False


def is_valid_name(name: str) -> bool:
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
