@0xc0dec67602a1c0ec;

using import "client.capnp".Client;
using import "server.capnp".Server;

interface Login {
    connect @0 (client :Client, name :Text) -> (server :Server, handle :LoginHandle);

    interface LoginHandle {}
}
