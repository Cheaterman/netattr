#!/usr/bin/env python3

import capnp
from netattr.capnp import entity_capnp
from netattr.entity import Property
from netattr.server import Player, App


class TestPlayer(Player):
    coords = Property(
        entity_capnp.EntityProperty.Coords.new_message(x=.5, y=.5)
    )
    movementSpeed = Property(450)
    radius = Property(45)

    def __init__(self, server, **kwargs):
        super().__init__(server, **kwargs)
        self.current_actions = []

    def do(self, action, **kwargs):
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


class TestServer(App):
    player_class = TestPlayer

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


if __name__ == '__main__':
    TestServer().run()
