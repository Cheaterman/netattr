#!/usr/bin/env python3

import time
import uuid

import capnp
import entity_capnp
import client_capnp
import command_capnp
import login_capnp
import server_capnp

from netattr.entity import ObservableEntity, ObservableProperty


class Login(login_capnp.Login.Server):
    def __init__(self):
        self.server = ServerApp.get_running_server()

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
    def __init__(self, client, server):
        self.client = client
        self.server = server

    def join(self, _context):
        player = Player(self)
        self.server.spawn(player)
        return player

    def send(self, command, _context):
        pass


class Player(ObservableEntity, server_capnp.Player.Server):
    name = ObservableProperty()
    coords = ObservableProperty(
        entity_capnp.EntityProperty.Coords.new_message(x=.5, y=.5)
    )
    movementSpeed = ObservableProperty(450)
    radius = ObservableProperty(45)

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

        self.current_actions = []

    def update_clients(self, prop, value):
        for client in self.clients.values():
            client.update(entity_capnp.EntityProperty.new_message(
                **{prop: value}
            ))

    def do(self, action, _context):
        if action.startswith(('+', '-')):
            reverse_action = False

            if action[0] == '-':
                reverse_action = True

            action = action[1:]

        if not reverse_action:
            if action not in self.current_actions:
                self.current_actions.append(action)
        else:
            if action in self.current_actions:
                self.current_actions.remove(action)


class Client(object):
    def __init__(self, address, client_handle, name):
        self.address = address
        self.client_handle = client_handle
        self.name = name

    def send(self, command):
        return self.client_handle.send(command)

    def create(self, entity):
        return self.client_handle.create(entity)


class ServerApp(object):
    _running_server = None

    def __init__(self, **kwargs):
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
        Coords = entity_capnp.EntityProperty.Coords

        for player in self.players:
            movement_speed = (
                player.movementSpeed / 100. * 1. / self.sv_fps
            )

            for action in player.current_actions[:]:
                coord_x, coord_y = player.coords.x, player.coords.y
                if action == 'up':
                    coord_y += movement_speed
                if action == 'down':
                    coord_y -= movement_speed
                if action == 'right':
                    coord_x += movement_speed
                if action == 'left':
                    coord_x -= movement_speed
                player.coords = Coords.new_message(x=coord_x, y=coord_y)

                if action == 'bomb':
                    player.current_actions.remove('bomb')
                    # TODO: Do this :)

                    #level = player.level
                    #tile = level.tile_at(*level.coords(*player.center))
                    #if any([bomb.tile is tile for bomb in level.bombs]):
                    #    continue
                    #bomb = Bomb(
                    #    level=level,
                    #    tile=tile,
                    #    owner=player,
                    #)
                    #level.add_widget(bomb, index=1)

    def run(self):
        listen_address = '%s:%d' % (self.address, self.port)
        self.server = capnp.TwoPartyServer(
            listen_address,
            bootstrap=Login,
        )
        print('Listening on %s' % listen_address)
        tick_duration = 1. / self.sv_fps
        type(self)._running_server = self

        while True:
            self.update()
            start_time = time.time()
            capnp.getTimer().after_delay(tick_duration).wait()
            time.sleep(tick_duration - (time.time() - start_time))

    @classmethod
    def get_running_server(cls):
        return cls._running_server


if __name__ == '__main__':
    server = ServerApp()
    server.run()
