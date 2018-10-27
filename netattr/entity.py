class PropertyStorage:
    def __init__(self, value):
        self.value = value
        self.observers = []


class Property:
    def __init__(self, default_value=None):
        self.default_value = default_value
        self.name = ''
        self.instance = None

    def __repr__(self):
        return '<Property {}>'.format(
            '{} of {}'.format(self.name, self.instance)
            if self.name and self.instance else '(unbound)'
        )

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__storage[self.name].value

    def __set__(self, instance, value):
        storage = instance.__storage[self.name]

        if value != storage.value:
            storage.value = value

            for callback in storage.observers:
                callback(instance, value)

    def link(self, instance, name):
        self.name = name
        self.instance = instance

        try:
            instance.__storage
        except AttributeError:
            instance.__storage = {}

        instance.__storage[name] = PropertyStorage(self.default_value)

    def bind(self, callback):
        self.instance.__storage[self.name].observers.append(callback)


class ObservableMeta(type):
    def __new__(cls, name, bases, attrs):
        result = super(ObservableMeta, cls).__new__(cls, name, bases, attrs)

        def _property(self, name):
            return self.__properties[name]

        def _properties(self):
            return dict(self.__properties)

        result.property = _property
        result.properties = _properties

        return result

    def __init__(self, name, bases, attrs):
        attrs.update({
            attr: value
            for base in bases
            for attr, value in vars(base).items()
            if isinstance(value, Property)
        })

        properties = {}

        for name, prop in attrs.items():
            if isinstance(prop, Property):
                prop.link(self, name)
                properties[name] = prop

        try:
            self.__properties.update(properties)
        except AttributeError:
            self.__properties = properties



class Observable(metaclass=ObservableMeta):
    def bind(self, **kwargs):
        for prop, callback in kwargs.items():
            self.property(prop).bind(callback)
