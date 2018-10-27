#!/usr/bin/env python3

import sys

from netattr.client import App


class TestClient(App):
    def create_entity(self, entity):
        handle = super().create_entity(entity)
        print('Create entity: {0.name}'.format(handle))
        return handle

    def update_entity(self, entity, prop):
        print('Update entity: {0.name}, {1}'.format(entity, prop))

    def update(self):
        do = self.player.do
        delay = self.delay

        do('+up')
        delay(1)
        do('-up')
        delay(1)
        do('+down')
        delay(1)
        do('-down')
        delay(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} name'.format(sys.argv[0]))
        sys.exit(1)

    client = TestClient(
        address='127.0.0.1',
        port=25000,
        name=sys.argv[1],
    )
    client.run()
