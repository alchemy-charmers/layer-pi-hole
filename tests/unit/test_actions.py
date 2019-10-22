from importlib.machinery import SourceFileLoader


class TestActions:
    def test_restart_dns(self, pihole):
        SourceFileLoader("actions", "./actions/restart-dns").load_module()
        assert pihole.mock_subprocess.check_call.call_count == 1

    def test_update(self, pihole):
        SourceFileLoader("actions", "./actions/update").load_module()
        assert pihole.mock_subprocess.check_call.call_count == 1
