import socket

from charmhelpers.core import hookenv, templating


class PiholeHelper:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.setup_vars_file = "/etc/pihole/setupVars.conf"
        self.stubby_file = "/etc/stubby/stubby.yml"
        self.stubby_service = "stubby.service"
        self.unbound_file = "/etc/unbound/unbound.conf.d/pihole.conf"
        self.unbound_service = "unbound.service"
        self.ftl_service = "pihole-FTL.service"
        self.pihole_extra_file = "/etc/dnsmasq.d/02-pihole-extra.conf"
        self.stubby_port = 532
        self.unbound_port = 531

    def action_function(self):
        """ An example function for calling from an action """
        return

    def preconfig(self, interface, ipv4="", ipv6="", no_custom=False):
        """ Create setupVars.conf for unattended install """
        # https://discourse.pi-hole.net/t/what-is-setupvars-conf-and-how-do-i-use-it/3533

        dns = self.charm_config["dns-addresses"].split(";")
        dns_addresses = ["", "", "", ""]
        if self.charm_config["enable-recursive-dns"] and not no_custom:
            dns_addresses[0] = "127.0.0.1#{}".format(self.unbound_port)
        elif self.charm_config["enable-dns-over-tls"] and not no_custom:
            dns_addresses[0] = "127.0.0.1#{}".format(self.stubby_port)
        else:
            for index, address in enumerate(dns):
                dns_addresses[index] = address
        temp_units = "F"
        if self.charm_config["temperature-units"] == "C":
            temp_units = "C"
        context = {
            "interface": interface,
            "ipv4_address": ipv4,
            "ipv6_address": ipv6,
            "dns1": dns_addresses[0],
            "dns2": dns_addresses[1],
            "dns3": dns_addresses[2],
            "dns4": dns_addresses[3],
            "temp_unit": temp_units,
        }
        templating.render("setupVars.conf.j2", self.setup_vars_file, context)
        return

    def configure_stubby(self):
        context = {"port": self.stubby_port}
        templating.render("stubby.yml.j2", self.stubby_file, context)

    def configure_unbound(self):
        context = {"port": self.unbound_port}
        if self.charm_config["enable-dns-over-tls"]:
            context["stubby_port"] = self.stubby_port
        templating.render("pihole.conf", self.unbound_file, context)

    def configure_conditional_forwards(self):
        forwards = []
        for entry in self.charm_config["conditional-forwards"].split(","):
            if len(entry):
                forwards.append(entry.split(":"))
        context = {"forwards": forwards, "num_forwards": len(forwards)}
        templating.render("02-pihole-extra.conf.j2", self.pihole_extra_file, context)

    def configure_proxy(self, proxy):
        """Configure Pi-Hole for operation behind a reverse proxy."""
        proxy_config = [
            {
                "mode": "http",
                "external_port": self.charm_config["proxy-external-port"],
                "internal_host": socket.getfqdn(),
                "internal_port": 80,
                "subdomain": self.charm_config["proxy-subdomain"],
                "acl-local": self.charm_config["proxy-local"],
            }
        ]
        proxy.configure(proxy_config)
