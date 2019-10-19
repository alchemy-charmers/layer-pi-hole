import subprocess
import urllib.request

from charmhelpers import fetch
from charmhelpers.core import hookenv, host
from charms.reactive import clear_flag, endpoint_from_name, set_flag, when, when_not
from lib_pi_hole import PiholeHelper

helper = PiholeHelper()
HEALTHY = "Pi-Hole installed and configured"


@when_not("pi-hole.preconfig")
def preconfig_pi_hole():
    # TODO: detect this interface
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip())
    set_flag("pi-hole.preconfig")


@when_not("pi-hole.installed")
@when("pi-hole.preconfig", "stubby.configured")
def install_pi_hole():
    hookenv.status_set("maintenance", "Installing pihole")
    urllib.request.urlretrieve("https://install.pi-hole.net", "install.sh")
    subprocess.check_call(["chmod", "+x", "./install.sh"], stderr=subprocess.STDOUT)
    subprocess.check_call(
        ["sudo", "./install.sh", "--unattended"], stderr=subprocess.STDOUT
    )
    hookenv.status_set("active", HEALTHY)
    set_flag("pi-hole.installed")


@when_not("stubby.installed")
def install_stubby():
    fetch.apt_install("stubby")
    hookenv.status_set("maintenance", "Installing stubby")
    set_flag("stubby.installed")


@when("stubby.installed")
@when_not("stubby.configured")
def configure_stubby():
    helper.configure_stubby()
    host.service_restart(helper.stubby_service)
    hookenv.status_set("maintenance", "Configuring stubby")
    set_flag("stubby.configured")


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
