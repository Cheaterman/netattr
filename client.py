#!/usr/bin/env python3

import sys

import capnp
import client_capnp
import entity_capnp
import login_capnp


class EntityHandle(entity_capnp.EntityHandle.Server):
    def __init__(self, app, type, props):
        self.app = app
        self.type = type
        for name, value in (list(prop.items())[0] for prop in props):
            setattr(self, name, value)

    def update(self, property, _context):
        name, value = list(property.to_dict().items())[0]
        setattr(self, name, value)
        self.app.update_entity(self, property)


class Client(client_capnp.Client.Server):
    def __init__(self, app):
        self.app = app

    def send(self, command, _context):
        self.app.do_command(command)

    def create(self, entity, _context):
        return self.app.create_entity(entity)


class ClientApp(object):
    def __init__(self):
        self.entities = []

    def run(self, address, name):
        self.capnp_client = capnp_client = capnp.TwoPartyClient(address)
        self.login = login = capnp_client.bootstrap().cast_as(
            login_capnp.Login
        )

        self.client = client = Client(self)
        response = login.connect(client, name).wait()

        self.server = server = response.server
        self.login_handle = response.handle

        self.player = player = server.join().wait().player

        while True:
            def delay_for(seconds):
                import time
                start_time = time.time()
                while time.time() < start_time + seconds:
                    capnp.getTimer().after_delay(1 / 60.).wait()

            player.do('+up').wait()
            delay_for(1)
            player.do('-up').wait()
            delay_for(1)
            player.do('+down').wait()
            delay_for(1)
            player.do('-down').wait()
            delay_for(1)

    def do_command(self, command):
        print('do_command', command)

    def create_entity(self, entity):
        handle = EntityHandle(self, **entity.to_dict())
        self.entities.append(handle)

        print('create_entity', vars(handle))

        return handle

    def update_entity(self, entity_handle, prop):
        print('update_entity', vars(entity_handle))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} name'.format(sys.argv[0]))
        sys.exit(1)

    client = ClientApp()
    client.run('127.0.0.1:25000', sys.argv[1])
