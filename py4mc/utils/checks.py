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
    # Mojang does not complain with names under 3 chars long.
    # 25 is the limit before Mojang starts throwing errors.
    if len(name) <= 25:
        return all(x in ascii_letters + "_" for x in name)
    return False

