from abc import ABC, abstractmethod
from typing import List, Any

class IRepository(ABC):
    @abstractmethod
    def create(self, item: Any) -> Any: pass
    @abstractmethod
    def get_all(self) -> List[Any]: pass
    @abstractmethod
    def update(self, item: Any) -> bool: pass
    @abstractmethod
    def delete(self, item_id: int) -> bool: pass
    @abstractmethod
    def get_by_id(self, item_id: int) -> Any: pass