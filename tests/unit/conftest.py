#!/usr/bin/python3
import mock
import pytest


# If layer options are used, add this to pihole
# and import layer in lib_pi_hole
@pytest.fixture
def mock_layers(monkeypatch):
    import sys
    sys.modules['charms.layer'] = mock.Mock()
    sys.modules['reactive'] = mock.Mock()
    # Mock any functions in layers that need to be mocked here

    def options(layer):
        # mock options for layers here
        if layer == 'example-layer':
            options = {'port': 9999}
            return options
        else:
            return None

    monkeypatch.setattr('lib_pi_hole.layer.options', options)


@pytest.fixture
def mock_hookenv_config(monkeypatch):
    import yaml

    def mock_config():
        cfg = {}
        yml = yaml.load(open('./config.yaml'))

        # Load all defaults
        for key, value in yml['options'].items():
            cfg[key] = value['default']

        # Manually add cfg from other layers
        # cfg['my-other-layer'] = 'mock'
        return cfg

    monkeypatch.setattr('lib_pi_hole.hookenv.config', mock_config)


@pytest.fixture
def mock_remote_unit(monkeypatch):
    monkeypatch.setattr('lib_pi_hole.hookenv.remote_unit', lambda: 'unit-mock/0')


@pytest.fixture
def mock_charm_dir(monkeypatch):
    monkeypatch.setattr('lib_pi_hole.hookenv.charm_dir', lambda: '/mock/charm/dir')


@pytest.fixture
def pihole(tmpdir, mock_hookenv_config, mock_charm_dir, monkeypatch):
    from lib_pi_hole import PiholeHelper
    helper = PiholeHelper()

    # Example config file patching
    cfg_file = tmpdir.join('example.cfg')
    with open('./tests/unit/example.cfg', 'r') as src_file:
        cfg_file.write(src_file.read())
    helper.example_config_file = cfg_file.strpath

    # Any other functions that load helper will get this version
    monkeypatch.setattr('lib_pi_hole.PiholeHelper', lambda: helper)

    return helper
