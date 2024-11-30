import os
import sys
from functools import wraps


def graceful_keyboard_interrupt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected. Exiting...")
            print("\nGoodbye! 👋\n")
            sys.exit(1)
    return wrapper


def debugger_on_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import pdb; pdb.set_trace()
            raise e
    return wrapper