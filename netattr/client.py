import capnp
import client_capnp


class CapnpClient(client_capnp.Client.Server):
    def __init__(self, client):
        self.client = client

    def send(self, command, _context):
        self.client.send(command)

    def create(self, entity, _context):
        self.client.create(entity)
