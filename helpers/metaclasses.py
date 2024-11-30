from helpers.cli_support import graceful_keyboard_interrupt, debugger_on_error


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
    
class GracefulInterruptMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # Wrap all public methods with graceful_keyboard_interrupt
        for key, value in attrs.items():
            if callable(value) and not key.startswith('_'):
                attrs[key] = graceful_keyboard_interrupt(value)
        return super().__new__(cls, name, bases, attrs)
    
    
class DebuggerOnErrorMetaclass(type):
    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if callable(value) and not key.startswith('_'):
                attrs[key] = debugger_on_error(value)
        return super().__new__(cls, name, bases, attrs)
