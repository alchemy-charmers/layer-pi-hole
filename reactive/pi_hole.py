from lib_pi_hole import PiholeHelper
from charmhelpers.core import hookenv
from charms.reactive import set_flag, when_not

helper = PiholeHelper()


@when_not('pi-hole.installed')
def install_pi_hole():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    hookenv.status_set('active', '')
    set_flag('pi-hole.installed')
