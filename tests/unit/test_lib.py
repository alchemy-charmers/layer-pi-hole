#!/usr/bin/python3


class TestLib():
    def test_pytest(self):
        assert True

    def test_pihole(self, pihole):
        ''' See if the helper fixture works to load charm configs '''
        assert isinstance(pihole.charm_config, dict)

    # Include tests for functions in lib_pi_hole
