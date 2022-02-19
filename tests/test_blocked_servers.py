import py4mc
import _hashlib

mojang = py4mc.MojangApi()


class TestBlockedServers:

    def test_blocked_servers(self):
        blocked_servers = mojang.get_blocked_servers()
        assert isinstance(blocked_servers, list)
        assert all([isinstance(b, str) for b in blocked_servers])

    def test_hashlibed_hashes(self):
        blocked_servers = mojang.get_blocked_servers(raw_hashes=False)
        assert isinstance(blocked_servers, list)
        assert all([isinstance(b, _hashlib.HASH) for b in blocked_servers])
