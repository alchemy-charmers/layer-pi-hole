from charmhelpers.core import hookenv, templating


class PiholeHelper:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.setup_vars_file = "/etc/pihole/setupVars.conf"

    def action_function(self):
        """ An example function for calling from an action """
        return

    def preconfig(self, interface, ipv4='', ipv6=''):
        """ Create setupVars.conf for unattended install """
        dns = self.charm_config["dns-addresses"].split(";")
        dns_addresses = ["", "", "", ""]
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
        # https://discourse.pi-hole.net/t/what-is-setupvars-conf-and-how-do-i-use-it/3533
        return
