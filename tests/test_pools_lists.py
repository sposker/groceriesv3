from logical.pools_and_lists import ItemPool, ListWriter
from tests.test_groups_items import itm0, itm1, itm2, itm3

item_set0 = {(itm0, '·', ''), (itm1, '2', ''), (itm2, '5', ''), }
item_set1 = {(itm2, '5', ''), (itm3, '·', '')}

pool0 = ItemPool(item_set0)
pool1 = ItemPool(item_set1)


class TestItemPool:

    def test_001_init(self):
        ...

    def test_002_merged(self):
        pool_merged = pool0 + pool1
        assert len(pool_merged) == 4








