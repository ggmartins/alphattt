import threading
from functools import wraps

def singleton(cls):
    """
    Thread-safe singleton decorator.

    - First call constructs the instance (under a lock).
    - Subsequent calls return the same instance.
    - Preserves class metadata (__name__, __doc__, etc.).
    """
    lock = threading.Lock()
    instance = None
    initialized = False  # avoids calling __init__ multiple times if you want

    @wraps(cls)
    def get_instance(*args, **kwargs):
        nonlocal instance, initialized
        if instance is not None:
            return instance

        with lock:
            if instance is None:
                instance = cls.__new__(cls)   # create object without running __init__
                if not initialized:
                    cls.__init__(instance, *args, **kwargs)  # run init once
                    initialized = True
        return instance

    # Expose original class if you want it for typing/introspection
    get_instance.__wrapped__ = cls
    return get_instance