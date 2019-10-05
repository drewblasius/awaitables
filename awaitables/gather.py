from concurrent.futures import Future
from typing import Any, List


def crummy_gather(*futures: Future) -> List[Any]:
    return [f.result() for f in futures]
