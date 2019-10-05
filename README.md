awaitables
===========

I got tired of dealing with asyncio stuff for a lot of things I was thinking about, and put together a little decorator that makes things "awaitable". Just for curiousity.

##### Usage:

```
from time import sleep, strftime

def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2    

def main():
    print(f"started at {strftime('%X')}")

    r1 = io_bound_process(2)
    r2 = io_bound_process(4)
    print(r1)
    print(r2)
    print(f"finished at {strftime('%X')}")

main()
```

has expected result

```
started at 17:13:52
1
2
finished at 17:13:54
```

Adding the `@awaitable` decorator, modifies the function to return a `concurrent.future.Future`.

```
from awaitables import awaitable
from time import sleep, strftime


# This wrapped function now returns a Future
@awaitable
def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2 

def main():
    print(f"started at {strftime('%X')}")

    r1 = io_bound_process(2)
    r2 = io_bound_process(4)
    print(r1.result())
    print(r2.result())
    print(f"finished at {strftime('%X')}")

main()
```

has expected result

```
started at 17:13:52
1
2
finished at 17:13:53
```

This has the advantage (I think) over asyncio's implementation that "asyncness" is no longer a property of the underlying function: e.g.


```
from awaitables import awaitable
from time import sleep, strftime

def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2 

def main():
    print(f"started at {strftime('%X')}")
    async_io_bound_process = awaitable(io_bound_process)
    r1 = io_bound_process(2)
    r2 = async_io_bound_process(4)
    r3 = async_io_bound_process(6)
    print(r1)
    print(r2.result())
    print(r3.result())
    print(f"finished at {strftime('%X')}")

main()
```

which has expected result

```
started at 17:13:52
1
2
3
finished at 17:13:54
```

Currently, the `@awaitable` decorator takes the following:

* No arguments, in which case the wrapped function has its own `ThreadPoolExecutor` instantiated, with the default args to `ThreadPoolExecutor`. eg.

```

# `io_bound_process` has its own ThreadPoolExecutor, instantiated via `ThreadPoolExecutor()`
@awaitable
def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2 

```

* Arguments and keyword arguments to `ThreadPoolExecutor`, in which case the wrapped function's `ThreadPoolExecutor` is instantiated with the passed arguments. eg.

```
# `io_bound_process` has its own ThreadPoolExecutor, instantiated via `ThreadPoolExecutor(max_workers=32)`
@awaitable(max_workers=32)
def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2 

```

* A `ThreadPoolExecutor` instance. eg.


```
shared_executor = ThreadPoolExecutor(max_workers=2)

@awaitable(shared_executor)
def io_bound_process(x: float) -> float:
    sleep(1)
    return x / 2 


@awaitable(shared_executor)
def other_io_bound_process(x: float) -> float:
    sleep(4)
    return x / 2 

# Now both functions share the same `ThreadPoolExecutor` instance.
```

