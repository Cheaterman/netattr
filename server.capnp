@0xe6ee6554a35cdc76;

using import "command.capnp".Command;

interface Server {
    join @0 () -> (player :Player);
    send @1 (command :Command);
}

interface Player {
    do @0 (action :Text);
}
