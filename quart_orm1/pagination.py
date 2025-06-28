from typing import List, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class Paginated(Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int

    def as_dict(self):
        return {
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "items": [
                item.as_dict() if hasattr(item, "as_dict") else str(item)
                for item in self.items
            ]
        }
