from abc import abstractmethod, ABC
from typing import List, Any


class BaseIterator(ABC):

    def __init__(self):
        self.current = 0
        self.page = 1
        self.size = 10
        self.list: List[Any] = []

    def next(self):
        if self.current >= len(self.list):
            return None
        else:
            self.current += 1
            return self.list[self.current - 1]

    async def hasNext(self):
        if self.current < len(self.list):
            return True

        self.list = await self.query()
        self.list = self.list if self.list else []
        self.current = 0
        self.page += 1
        return self.list is not None and len(self.list) > 0

    @abstractmethod
    async def query(self) -> List[Any]:
        pass


__all__ = [
    "BaseIterator",
]
