class PropertyStorage:
    def __init__(self, value):
        self.value = value
        self.observers = []


class NetworkedProperty:
    def __init__(self, default_value=None):
        self.default_value = default_value
        self.name = ''
        self.cls = None

    def __repr__(self):
        return '<NetworkedProperty {}>'.format(
            '{} of {}'.format(self.name, self.cls.__name__)
            if self.name and self.cls else '(unbound)'
        )

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.__storage[self.name].value
        else:
            return self

    def __set__(self, instance, value):
        if value != getattr(instance, self.name):
            instance.__storage[self.name].value = value
            print('Got change: {}.{} = {}'.format(
                instance.__class__.__name__,
                self.name,
                value
            ))

    def link(self, instance, name):
        self.name = name
        self.cls = instance.__class__

        if not hasattr(instance, '__storage'):
            instance.__storage = {}

        instance.__storage[name] = PropertyStorage(self.default_value)


class NetworkedEntity:
    def __new__(cls, *args, **kwargs):
        self = super(Base, cls).__new__(cls, *args, **kwargs)

        properties = {}

        for name, prop in cls.__dict__.items():
            if isinstance(prop, NetworkedProperty):
                prop.link(self, name)
                properties[name] = prop

        self.__properties = properties
        return self

    def property(self, name):
        return self.__properties[name]

    def properties(self):
        return dict(self.__properties)
