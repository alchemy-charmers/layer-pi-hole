#!/usr/bin/python3
import mock


class TestLib:
    def test_pytest(self):
        assert True

    def test_pihole(self, pihole):
        """ See if the helper fixture works to load charm configs """
        assert isinstance(pihole.charm_config, dict)

    def test_action_function(self, pihole):
        """ See if the example action can be caled """
        pihole.action_function()

    def test_preconfig_defaults(self, pihole):
        """ Verify the preconfig template generation """
        # Test with default config values
        pihole.preconfig(interface="eth0", ipv4="ipv4")
        with open(pihole.setup_vars_file, "rb") as var_file:
            print(pihole.setup_vars_file)
            content = var_file.readlines()
        assert b"PIHOLE_INTERFACE=eth0\n" in content
        assert b"IPV4_ADDRESS=ipv4\n" in content
        assert b"IPV6_ADDRESS=\n" in content
        assert b"PIHOLE_DNS_1=127.0.0.1#853\n" in content
        assert b"PIHOLE_DNS_2=\n" in content
        assert b"PIHOLE_DNS_3=\n" in content
        assert b"PIHOLE_DNS_4=\n" in content
        assert b"TEMPERATUREUNIT=F\n" in content

    def test_preconfig_no_tls(self, pihole):
        """ Verify the preconfig template generation """
        # Test with default config values
        pihole.charm_config["enable-dns-over-tls"] = False
        pihole.preconfig(interface="eth0", ipv4="ipv4")
        with open(pihole.setup_vars_file, "rb") as var_file:
            print(pihole.setup_vars_file)
            content = var_file.readlines()
            print(content)
        assert b"PIHOLE_INTERFACE=eth0\n" in content
        assert b"IPV4_ADDRESS=ipv4\n" in content
        assert b"IPV6_ADDRESS=\n" in content
        assert b"PIHOLE_DNS_1=1.1.1.1\n" in content
        assert b"PIHOLE_DNS_2=1.0.0.1\n" in content
        assert b"PIHOLE_DNS_3=2606:4700:4700::1111\n" in content
        assert b"PIHOLE_DNS_4=2606:4700:4700::1001\n" in content
        assert b"TEMPERATUREUNIT=F\n" in content

    def test_preconfig_custom(self, pihole):
        # Change DNS and temperature
        pihole.charm_config["enable-dns-over-tls"] = False
        pihole.charm_config["temperature-units"] = "C"
        pihole.charm_config["dns-addresses"] = "8.8.8.8;9.9.9.9"
        pihole.preconfig(interface="eth0", ipv4="ipv4", ipv6="ipv6")
        with open(pihole.setup_vars_file, "rb") as var_file:
            print(pihole.setup_vars_file)
            content = var_file.readlines()
        assert b"PIHOLE_INTERFACE=eth0\n" in content
        assert b"IPV4_ADDRESS=ipv4\n" in content
        assert b"IPV6_ADDRESS=ipv6\n" in content
        assert b"PIHOLE_DNS_1=8.8.8.8\n" in content
        assert b"PIHOLE_DNS_2=9.9.9.9\n" in content
        assert b"PIHOLE_DNS_3=\n" in content
        assert b"PIHOLE_DNS_4=\n" in content
        assert b"TEMPERATUREUNIT=C\n" in content

    def test_configure_stubby(self, pihole):
        pihole.configure_stubby()
        with open(pihole.stubby_file, "rb") as stubby_file:
            print(pihole.stubby_file)
            content = stubby_file.readlines()
            print(content)
        assert b"  - address_data: 1.1.1.1\n" in content
        assert b"  - address_data: 1.0.0.1\n" in content

    def test_proxy_config(self, pihole):
        proxy = mock.MagicMock()
        pihole.configure_proxy(proxy)
        print(dir(proxy))
        print(proxy.method_calls)
        print(dir(proxy.configure))
        config = [
            {
                "mode": "http",
                "external_port": 443,
                "internal_host": "mock-host",
                "internal_port": 80,
                "subdomain": "pihole",
                "acl-local": True,
            }
        ]
        proxy.configure.assert_called_with(config)

    # Include tests for functions in lib_pi_hole
