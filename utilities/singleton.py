from weakref import WeakValueDictionary


class Singleton(type):
    """
    Metaclass for making the Singleton design pattern work
    @attention The way in which the singleton is built by this metaclass is based only
    on the name of the class being manage by the pattern.
    Different class parameters will be ignore when considering if this metaclass will serve
    a new class instance or not
    """

    def __init__(cls, class_name, bases, class_dict):
        super().__init__(class_name, bases, class_dict)
        cls._cache = WeakValueDictionary()
        cls._cache[class_name] = object

    def __call__(cls, *args, **kwargs):
        class_name = cls.__name__
        if cls._cache[class_name] is not object:
            return cls._cache[class_name]
        else:
            obj = super().__call__(*args, **kwargs)
            cls._cache[class_name] = obj
            return obj
