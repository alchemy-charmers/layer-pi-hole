import subprocess
import urllib.request

from charmhelpers import fetch
from charmhelpers.core import hookenv, host
from charms.reactive import clear_flag, endpoint_from_name, set_flag, when, when_not
from lib_pi_hole import PiholeHelper

helper = PiholeHelper()
HEALTHY = "Pi-Hole installed and configured"


# @when_not("pi-hole.preconfig")
# def preconfig_pi_hole():
#     # TODO: detect this interface
#     helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip(), no_custom=True)
#     set_flag("pi-hole.preconfig")


@when_not("pi-hole.installed")
@when("stubby.installed")
def install_pi_hole():
    hookenv.status_set("maintenance", "Installing pihole")
    # Ignore custom upstream, unbound will be installe dafter pi-hole
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


# @when("stubby.installed")
# @when_not("stubby.configured")
# def configure_stubby():
#     hookenv.status_set("maintenance", "Configuring stubby")
#     helper.configure_stubby()
#     host.service_restart(helper.stubby_service)
#     set_flag("stubby.configured")


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
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip())
    subprocess.check_call(
        ["sudo", "./install.sh", "--reconfigure", "--unattended"],
        stderr=subprocess.STDOUT,
    )
    set_flag("pi-hole.configured")
    hookenv.status_set("active", HEALTHY)


# @when("unbound.installed")
# @when_not("unbound.configured")
# def configure_unbound():
#     hookenv.status_set("maintenance", "Configureing unbound")
#     helper.configure_unbound()
#     host.service_restart(helper.unbound_service)
# set_flag("unbound.configured")


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
