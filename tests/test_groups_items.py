from logical.groups_and_items import DisplayGroup, GroceryItem

grp0 = DisplayGroup('Deli')
grp1 = DisplayGroup('Bakery', uid=4)
grp2 = DisplayGroup('Aisle 06', uid='g06')

itm0 = GroceryItem(name='Pasta', group=grp0)
itm1 = GroceryItem(name='Bagels', uid='i099', group=grp1.uid)
itm2 = GroceryItem(name='Donuts', group='Bakery', note='with sprinkles')
itm3 = GroceryItem(name='Ice Cream', group=grp2, defaults=[(10000, '2'), (20000, '')])


class TestDisplayGroup:

    def test_001_group_name(self):
        assert grp0.name == 'Deli'
        assert grp1.name == 'Bakery'
        assert grp2.name == 'Aisle 06'

    def test_002_group_uid(self):
        assert grp0.uid == 'g00'
        assert grp1.uid == 'g04'
        assert grp2.uid == 'g06'
        
    def test_003_group_sorting(self):
        assert sorted({grp1, grp0, grp2}) == [grp0, grp1, grp2]


class TestGroceryItem:

    def test_001_item_name(self):
        assert itm0.name == 'Pasta'
        assert itm1.name == 'Bagels'
        assert itm2.name == 'Donuts'
        assert itm3.name == 'Ice Cream'

    def test_002_item_group(self):
        assert itm0.group.uid == 'g00'
        assert itm1.group.uid == 'g04'
        assert itm2.group.uid == 'g04'
        assert itm3.group.uid == 'g06'

    def test_003_item_note(self):
        for item in [itm0, itm1, itm3]:
            assert item.note == ''
        assert itm2.note == 'with sprinkles'

    def test_004_item_defaults(self):
        t = round(itm0.defaults[0][0])
        for item in [itm0, itm1, itm2]:
            assert len(item.defaults) == 1
            assert round(item.defaults[0][0]) == t or round(item.defaults[0][0]) + 1 == t
        assert len(itm3.defaults) == 2
        assert [k for k, _ in itm3.defaults] == [10000, 20000]

    def test_005_item_sort(self):
        assert sorted({itm3, itm0, itm1, itm2}) == [itm0, itm2, itm3, itm1]



