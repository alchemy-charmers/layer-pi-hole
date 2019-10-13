import subprocess

from charmhelpers.core import hookenv
from charms.reactive import set_flag, when_not
from lib_pi_hole import PiholeHelper

helper = PiholeHelper()


@when_not("pi-hole.preconfig")
def preconfig_pi_hole():
    helper.preconfig(interface="eth0", ipv4=hookenv.unit_public_ip())
    set_flag("pi-hole.preconfig")


@when_not("pi-hole.installed")
def install_pi_hole():
    cmd = [
        "curl",
        "-L",
        "https://install.pi-hole.net",
        "|",
        "bash",
        "/dev/stdin",
        "--unattended",
    ]
    subprocess.check_call(cmd, stderror=subprocess.STDOUT, shell=True)
    hookenv.status_set("active", "")
    set_flag("pi-hole.installed")
