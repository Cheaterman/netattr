#!/usr/bin/env python3

import sys
import time

import capnp
from netattr.capnp import client_capnp
from netattr.capnp import entity_capnp
from netattr.capnp import login_capnp


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


class App(object):
    def __init__(self, **kwargs):
        self.address = kwargs.pop('address', '')
        self.port = kwargs.pop('port', 0)
        self.name = kwargs.pop('name', '')
        self.fps = kwargs.pop('fps', 60)
        self.entities = []

    def run(self, address=None, port=None, name=None):
        if address is None or port is None:
            address = self.address
            port = self.port

            if not address or not port:
                raise ValueError(
                    'Cannot run App without address and port!'
                )

        if name is None:
            name = self.name

            if not name:
                raise ValueError(
                    'Cannot run App without a name!'
                )

        connection_address = '{}:{}'.format(self.address, self.port)

        self.capnp_client = capnp_client = capnp.TwoPartyClient(
            connection_address
        )
        self.login = login = capnp_client.bootstrap().cast_as(
            login_capnp.Login
        )

        self.client = client = Client(self)
        response = login.connect(client, name).wait()

        self.server = server = response.server
        self.login_handle = response.handle

        self.player = server.join().wait().player

        while True:
            self.update()
            capnp.getTimer().after_delay(1 / self.fps).wait()

    def update(self):
        pass

    def delay(self, seconds):
        start_time = time.time()
        while time.time() < start_time + seconds:
            capnp.getTimer().after_delay(1 / self.fps).wait()

    def do_command(self, command):
        pass

    def create_entity(self, entity):
        handle = EntityHandle(self, **entity.to_dict())
        self.entities.append(handle)

        return handle

    def update_entity(self, entity_handle, prop):
        pass
