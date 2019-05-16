from functools import wraps
import inspect


def initializer(func):
    spec_obj = inspect.getfullargspec(func)
    names, varargs, keywords, defaults = spec_obj.args, spec_obj.varargs, spec_obj.varkw, spec_obj.defaults

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for name, arg in list(zip(names[1:], args)) + list(kwargs.items()):
            setattr(self, name, arg)
        if defaults is not None:
            for i in range(len(defaults)):
                index = -(i + 1)
                if not hasattr(self, names[index]):
                    setattr(self, names[index], defaults[index])
        func(self, *args, **kwargs)

    return wrapper
