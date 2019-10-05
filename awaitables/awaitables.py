from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial, wraps
from typing import Callable


def awaitable(*executor_args, **executor_kwargs):

    def _awaitable(func: Callable, executor: ThreadPoolExecutor) -> Callable:

        @wraps(func)
        def wrapper(*args, **kwargs) -> Future:
            result = executor.submit(func, *args, **kwargs)
            return result

        return wrapper

    # guard for bare decorator case
    if len(executor_args) == 1 and callable(executor_args[0]):
        executor = ThreadPoolExecutor()
        func = executor_args[0]
        return _awaitable(func, executor)

    if len(executor_args) == 1 and isinstance(executor_args[0], ThreadPoolExecutor):
        executor = executor_args[0]
    else:
        executor = ThreadPoolExecutor(*executor_args, **executor_kwargs)

    return partial(_awaitable, executor=executor)
