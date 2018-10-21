from kivy.event import EventDispatcher
import capnp
import bomberman_capnp


class CapnpClient(bomberman_capnp.Client.Server):
    def __init__(self, client):
        self.client = client

    def send(self, command, _context):
        self.client.send(command)

    def create(self, entity, _context):
        self.client.create(entity)


class Client(EventDispatcher):
    __events__ = (
        'on_create',
        'on_command',  # Binds to all unknown commands (ones not below)
        # List of all possible commands
        'on_say',
    )

    def __init__(self):
        self.capnp_client = CapnpClient(self)

    def send(self, command):
        event_name, args = 'on_%s' % command.name, command.args
        if self.is_event_type(event_name):
            self.dispatch(event_name, *args)
        else:
            self.dispatch('on_command', command.name, *args)

    def create(self, entity):
        self.dispatch('on_create', entity)

    def on_create(self, entity):
        pass

    def on_command(self, client, command, *args):
        pass

    def on_say(self, client, sender, content):
        pass
