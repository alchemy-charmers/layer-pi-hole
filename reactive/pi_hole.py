import subprocess
import urllib.request

from charmhelpers import fetch
from charmhelpers.core import hookenv, host
from charms.reactive import clear_flag, endpoint_from_name, set_flag, when, when_not
from lib_pi_hole import PiholeHelper

helper = PiholeHelper()
HEALTHY = "Pi-Hole installed and configured"


@when_not("pi-hole.installed")
@when("stubby.installed")
def install_pi_hole():
    hookenv.status_set("maintenance", "Installing pihole")
    # Ignore custom upstream, unbound will be installed after pi-hole and
    # then we can add stubby and unbound to pihole
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip(), no_custom=True)
    urllib.request.urlretrieve("https://install.pi-hole.net", "install.sh")
    subprocess.check_call(["chmod", "+x", "./install.sh"], stderr=subprocess.STDOUT)
    subprocess.check_call(
        ["sudo", "./install.sh", "--unattended"], stderr=subprocess.STDOUT
    )
    set_flag("pi-hole.installed")


@when_not("stubby.installed")
def install_stubby():
    hookenv.status_set("maintenance", "Installing stubby")
    fetch.apt_install("stubby")
    helper.configure_stubby()
    host.service_restart(helper.stubby_service)
    set_flag("stubby.installed")


@when_not("unbound.installed")
@when("pi-hole.installed")
def install_unbound():
    hookenv.status_set("maintenance", "Installing unbound")
    fetch.apt_install("unbound")
    hookenv.status_set("maintenance", "Configuring unbound")
    host.service_stop(helper.unbound_service)
    helper.configure_unbound()
    host.service_start(helper.unbound_service)
    set_flag("unbound.installed")


@when("unbound.installed", "pi-hole.installed")
@when_not("pi-hole.configured")
def configure_pihole():
    """ Rerun install to reconfigure pihole"""
    hookenv.status_set("maintenance", "Configuring pi-hole")
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip())
    helper.configure_conditional_forwards()
    subprocess.check_call(
        ["sudo", "./install.sh", "--reconfigure", "--unattended"],
        stderr=subprocess.STDOUT,
    )
    set_flag("pi-hole.configured")
    hookenv.status_set("active", HEALTHY)


@when("config.changed.conditional-forwards", "pi-hole.configured")
def configure_conditional_forwards():
    """ Configure local forarding if provided """
    hookenv.log("Reconfiguring conditional forwards")
    helper.configure_conditional_forwards()
    host.service_restart(helper.ftl_service)


@when("config.changed.enable-recursive-dns", "pi-hole.configured")
def reconfigure_recursive():
    # Chaning recrusive is only a matter of updating pi-hole config to use or
    # not use unbound
    configure_pihole()


@when("config.changed.enable-dns-over-tls", "pi-hole.configured")
def reconfigure_dns_over_tls():
    # Pi-hole or unbound could be using stubby, both need to be updated to match
    # the configuration.

    # Update Unbound configuration to use or not use tls
    helper.configure_unbound()
    host.service_restart(helper.unbound_service)

    # Update pi-hole configuration
    configure_pihole()


@when("reverseproxy.ready")
@when_not("reverseproxy.configured")
def setup_proxy():
    """Configure reverse proxy settings when haproxy is related."""
    hookenv.status_set("maintenance", "Applying reverse proxy configuration")
    hookenv.log("Configuring reverse proxy via: {}".format(hookenv.remote_unit()))

    interface = endpoint_from_name("reverseproxy")
    hookenv.log("Using interface: {}".format(interface))
    hookenv.log("Interface: {}".format(dir(interface)))
    helper.configure_proxy(interface)

    hookenv.status_set("active", HEALTHY)
    set_flag("reverseproxy.configured")


@when("reverseproxy.departed")
def remove_proxy():
    """Remove the haproxy configuration when the relation is removed."""
    hookenv.status_set("maintenance", "Removing reverse proxy relation")
    hookenv.log("Removing config for: {}".format(hookenv.remote_unit()))

    hookenv.status_set("active", HEALTHY)
    clear_flag("reverseproxy.configured")
