class PropertyStorage:
    def __init__(self, value):
        self.value = value
        self.observers = []


class ObservableProperty:
    def __init__(self, default_value=None):
        self.default_value = default_value
        self.name = ''
        self.instance = None

    def __repr__(self):
        return '<ObservableProperty {}>'.format(
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


class ObservableEntity:
    def __new__(cls, *args, **kwargs):
        result = super(ObservableEntity, cls).__new__(cls, *args, **kwargs)

        properties = {}

        for name, prop in vars(cls).items():
            if isinstance(prop, ObservableProperty):
                prop.link(result, name)
                properties[name] = prop

        result.__properties = properties

        return result

    def property(self, name):
        return self.__properties[name]

    def properties(self):
        return dict(self.__properties)

    def bind(self, **kwargs):
        for prop, callback in kwargs.items():
            self.__properties[prop].bind(callback)
