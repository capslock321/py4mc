import hashlib

from ..dispatcher import Dispatch


class _Texture:
    def __init__(self, texture_url: str):
        self.texture = self._texture_bytes(texture_url)
        self.texture_url = texture_url
        # It's less intensive to just get the last 38 characters
        # rather than to hash the bytes.
        self.texture_hash = texture_url[38:]

    def __str__(self):
        return self.texture_hash

    def __eq__(self, other: object):
        if type(self) != type(other):
            return False
        return self.texture_hash == other.texture_hash

    def _texture_bytes(self, texture_url: str):
        response = Dispatch.do_request("GET", texture_url)
        return response.content


class Skin(_Texture):
    def __init__(self, texture_url: str, model_type: str):
        super().__init__(texture_url)
        self.model = model_type

    def __repr__(self):
        return f"<{self.__class__.__name__} model={self.model}>"


class Cape(_Texture):
    pass

