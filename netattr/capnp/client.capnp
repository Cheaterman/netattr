@0x972b8da5df3e325e;

using import "command.capnp".Command;
using import "entity.capnp".Entity;
using import "entity.capnp".EntityHandle;

interface Client {
    send @0 (command :Command);
    create @1 (entity :Entity) -> (handle :EntityHandle);
}
