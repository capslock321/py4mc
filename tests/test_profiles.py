import os
import py4mc

from collections.abc import Iterable

from py4mc.types.profile import Profile, HistoryIndex
from py4mc.types.textures import Skin, Cape

mojang = py4mc.MojangApi()

PATH = os.path.dirname(os.path.realpath(__file__))


class TestProfiles:
    def test_single_profile(self):
        profile = mojang.get_profile("capslock321")
        assert profile is not None
        assert isinstance(profile, Profile)
        assert isinstance(profile.get_skin(), Skin)
        if profile.get_cape() is not None:
            assert isinstance(profile.get_cape(), Cape)
        assert profile.default_skin() == "Steve"

    def test_profiles(self):
        test_profiles = open(PATH + "\\assets\\test_profiles.txt", "r").read()
        profiles = mojang.get_profile(test_profiles.splitlines())
        assert isinstance(profiles, Iterable)
        assert all([isinstance(p, Profile) for p in profiles])

    def test_invalid_profiles(self):
        test_profiles = open(PATH + "\\assets\\test_profiles_invalid.txt", "r").read()
        profiles = mojang.get_profile(test_profiles.splitlines())
        assert isinstance(profiles, Iterable)
        assert all([isinstance(p, type(None)) for p in profiles])

    def test_name_history(self):
        test_profiles = mojang.get_profile(["Notch", "dog"])
        for profile in test_profiles:
            history = profile.name_history()
            if isinstance(history, list):
                assert all([isinstance(h, HistoryIndex) for h in history])
            else:
                assert isinstance(history, HistoryIndex)


if __name__ == "__main__":
    profiles = open("./assets/test_profiles.txt", "r").read()
    print(profiles.splitlines())
