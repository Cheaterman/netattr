#!/usr/bin/env python3

import time
import uuid

import capnp
from netattr.capnp import entity_capnp
from netattr.capnp import client_capnp
from netattr.capnp import command_capnp
from netattr.capnp import login_capnp
from netattr.capnp import server_capnp

from netattr.entity import Observable, Property


class Login(login_capnp.Login.Server):
    def __init__(self):
        self.server = App.get_running_app()

    def connect(self, client, name, _context):
        if not self.server.validate_login(self.address, name):
            raise ValueError('Invalid username or client already connected.')

        print('New user connected: %s (%s:%d)' % (name, *self.address))
        return self.server.connect(client, name, self)

    def on_connect(self, client):
        self.address = client
        print('New connection from: %s:%d' % client)

    def on_disconnect(self):
        print('User %s (%s:%d) disconnected.' % (
            self.server.clients[self.address].name, *self.address
        ))
        self.server.disconnect(self.address)


class LoginHandle(login_capnp.Login.LoginHandle.Server):
    def __init__(self, login):
        self.login = login

    def __del__(self):
        self.login.on_disconnect()


class Server(server_capnp.Server.Server):
    def __init__(self, client, app):
        self.client = client
        self.app = app

    def join(self, _context):
        player = self.app.player_class(self)
        self.app.spawn(player)
        return player

    def send(self, command, _context):
        pass


class Player(Observable, server_capnp.Player.Server):
    name = Property()

    def __init__(self, server):
        self.server = server
        self.clients = {}
        self.name = server.client.name

        props = [
            entity_capnp.EntityProperty.new_message(
                **{prop: getattr(self, prop)}
            )
            for prop in self.properties()
        ]

        self.entity = entity_capnp.Entity.new_message(
            type=entity_capnp.Entity.Type.player,
            props=props,
        )

        self.bind(**{
            prop: lambda _, value, prop=prop: self.update_clients(prop, value)
            for prop in self.properties()
        })

    def update_clients(self, prop, value):
        for client in self.clients.values():
            client.update(entity_capnp.EntityProperty.new_message(
                **{prop: value}
            ))

    def do(self, action, _context):
        pass


class Client(object):
    def __init__(self, address, client_handle, name):
        self.address = address
        self.client_handle = client_handle
        self.name = name

    def send(self, command):
        return self.client_handle.send(command)

    def create(self, entity):
        return self.client_handle.create(entity)


class App(object):
    player_class = Player

    _running_app = None

    def __init__(self, **kwargs):
        App._running_app = self
        self.address = kwargs.get('address', '0.0.0.0')
        self.port = kwargs.get('port', 25000)
        self.sv_fps = kwargs.get('sv_fps', 60)
        self.clients = {}
        self.players = []

    def validate_login(self, address, name):
        if address not in self.clients and self.validate_nickname(name):
            return True

    def validate_nickname(self, name):
        if(
            name and
            name not in [client.name for client in self.clients.values()]
        ):
            return True

    def connect(self, client_handle, name, login):
        client = Client(login.address, client_handle, name)
        self.clients[login.address] = client

        for player in self.players:
            player.clients[client] = client.create(player.entity).handle

        return Server(client, self), LoginHandle(login)

    def disconnect(self, address):
        for player in self.players[:]:
            if player.server.client.address == address:
                self.players.remove(player)

            del player.clients[self.clients[address]]

        del self.clients[address]

    def spawn(self, player):
        self.players.append(player)

        for client in self.clients.values():
            player.clients[client] = client.create(player.entity).handle

    def update(self):
        pass

    def run(self):
        listen_address = '%s:%d' % (self.address, self.port)
        self.server = capnp.TwoPartyServer(
            listen_address,
            bootstrap=Login,
        )
        print('Listening on %s' % listen_address)
        tick_duration = 1. / self.sv_fps

        while True:
            self.update()
            start_time = time.time()
            capnp.getTimer().after_delay(tick_duration).wait()
            time.sleep(tick_duration - (time.time() - start_time))

    @staticmethod
    def get_running_app():
        return App._running_app
