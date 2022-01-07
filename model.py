from dataclasses import dataclass
from datetime import date
from typing import Optional, NewType, List


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


Sku = NewType('Sku', str)


class Batch:
    def __init__(self, batch_id: str, sku: Sku, available: int, eta: Optional[date] = None):
        self.id = batch_id
        self.sku = sku
        self.available = available
        self.eta = eta

    def allocate(self, order_line: OrderLine):
        self.available -= order_line.quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.available >= order_line.quantity

    def prefer_than(self, shipping_batch) -> bool:
        if self.eta is None:
            return True
        if shipping_batch.eta is None:
            return False
        return self.eta > shipping_batch.eta

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    batch = next(
        b for b in sorted(batches) if b.can_allocate(line)
    )
    batch.allocate(line)
    return batch.id
