import subprocess
import urllib.request

from charmhelpers.core import hookenv
from charms.reactive import set_flag, when, when_not
from lib_pi_hole import PiholeHelper

helper = PiholeHelper()


@when_not("pi-hole.preconfig")
def preconfig_pi_hole():
    # TODO: detect this interface
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip())
    set_flag("pi-hole.preconfig")


@when_not("pi-hole.installed")
@when("pi-hole.preconfig")
def install_pi_hole():
    urllib.request.urlretrieve("https://install.pi-hole.net", "install.sh")
    subprocess.check_call(["chmod", "+x", "./install.sh"], stderr=subprocess.STDOUT)
    subprocess.check_call(
        ["sudo", "./install.sh", "--unattended"], stderr=subprocess.STDOUT
    )
    hookenv.status_set("active", "")
    set_flag("pi-hole.installed")
