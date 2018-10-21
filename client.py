#!/usr/bin/env python3

import sys

import capnp
import client_capnp
import entity_capnp
import login_capnp


class EntityHandle(entity_capnp.EntityHandle.Server):
    def __init__(self, app):
        self.app = app

    def update(self, property, _context):
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

        player.do('+up').wait()

        while True:
            capnp.getTimer().after_delay(1 / 60.).wait()

    def do_command(self, command):
        print('do_command', command)

    def create_entity(self, entity):
        print('create_entity', entity)

        handle = EntityHandle(self)
        self.entities.append(handle)

        return handle

    def update_entity(self, entity_handle, property):
        print('update_entity', property)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} name'.format(sys.argv[0]))

    client = ClientApp()
    client.run('127.0.0.1:25000', sys.argv[1])
