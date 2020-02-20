from logical.groups_and_items import DisplayGroup, GroceryItem

grp0 = DisplayGroup('Deli')
grp1 = DisplayGroup('Bakery', uid=4)
grp2 = DisplayGroup('Aisle 06', uid='g6')

itm0 = GroceryItem(name='Pasta', group=grp0)
itm1 = GroceryItem(name='Bagels', group=grp1.uid)
itm2 = GroceryItem(name='Donuts', group='Bakery', note='with sprinkles')
itm3 = GroceryItem(name='Ice Cream', group=grp2, defaults=[(10000, '2'), (20000, '')])


class TestDisplayGroup:

    def test_001(self):
        ...
        














