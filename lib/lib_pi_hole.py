from charmhelpers.core import hookenv


class PiholeHelper():
    def __init__(self):
        self.charm_config = hookenv.config()

    def action_function(self):
        ''' An example function for calling from an action '''
        return
