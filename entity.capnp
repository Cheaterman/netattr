@0xd904b3a7471d0981;

interface EntityHandle {
    # Can dynamically add props that were initially absent
    update @0 (property :EntityProperty);
}

struct Entity {
    type @0 :Type;

    # Initial state, may not contain all props, must not contain duplicates
    props @1 :List(EntityProperty);

    enum Type {
        player @0;
        bomb @1;
        item @2;
    }
}

struct EntityProperty {
    # Should describe all possible properties of all Entity.Types
    union {
        name @0 :Text;
        coords @1 :Coords;
        movementSpeed @2 :Float32;
        radius @3 :Float32;
    }

    struct Coords {
        x @0 :Float32;
        y @1 :Float32;
    }
}
