import datetime
from datetime import date, timedelta

from model import Batch, OrderLine, Sku, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = create_batch_n_order_line(Sku('RED-CHAIR'), 2, 10)
    batch.allocate(order_line)
    assert batch.available == 8


def create_batch_n_order_line(sku: Sku, quantity: int, available: int):
    batch = Batch(batch_id='BATCH-ID-001', sku=sku, available=available)
    order_line = OrderLine(order_id='ORDER-ID-001', sku=sku, quantity=quantity)
    return batch, order_line


def test_can_allocate_if_available_greater_than_required():
    large_batch, order_line = create_batch_n_order_line(Sku('RED-CHAIR'), 2, 10)
    assert large_batch.can_allocate(order_line)


def test_cannot_allocate_if_available_smaller_than_required():
    smaller_batch, order_line = create_batch_n_order_line(Sku('RED-CHAIR'), 12, 10)
    assert smaller_batch.can_allocate(order_line) is False


def test_can_allocate_if_available_equal_to_required():
    equal_batch, order_line = create_batch_n_order_line(Sku('RED-CHAIR'), 10, 10)
    assert equal_batch.can_allocate(order_line)


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch(batch_id='BATCH-ID-001', sku=Sku('RED-CHAIR'), available=10)
    shipping_batch = Batch(batch_id='BATCH-ID-001', sku=Sku('RED-CHAIR'), available=10,
                           eta=datetime.datetime.today() - timedelta(days=1))
    assert warehouse_batch.prefer_than(shipping_batch)


def test_prefers_earlier_batches():
    earlier_batch = Batch(batch_id='BATCH-ID-001', sku=Sku('RED-CHAIR'), available=10, eta=datetime.datetime.today())
    shipping_batch = Batch(batch_id='BATCH-ID-001', sku=Sku('RED-CHAIR'), available=10,
                           eta=datetime.datetime.today() - timedelta(days=1))
    assert earlier_batch.prefer_than(shipping_batch)


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch('in-stock-batch-ref', Sku('HIGHBROW-POSTER'), 100, eta=None)
    shipment_batch = Batch('shipment-batch-ref', Sku('HIGHBROW-POSTER'), 100, eta=tomorrow)
    line = OrderLine('oref', 'HIGHBROW-POSTER', 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.id
