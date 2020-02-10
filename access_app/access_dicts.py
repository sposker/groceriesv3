"""Contruct dicts for use in various AccessApp tabbed panel recycle views"""
from operator import itemgetter

from logical.database import Database
from logical.items import GroceryItem, DisplayGroup
from logical.stores import Store


class GroupDetail:
    """First tab layout; allows editing of group names and sort order"""

    def __init__(self, group: DisplayGroup):
        self.group = group

        self.kv_pairs = {
            'group_name': self.group.name,
            'group_uid': self.group.uid,
        }


class ItemDetail:
    """Second tab layout; allows editing of item details."""

    def __init__(self, item: GroceryItem):
        self.item = item

        defaults_list = self.item.defaults.copy()
        defaults_list.sort(key=itemgetter(0))
        defaults_list = [str(num) for _, num in defaults_list]
        while len(defaults_list) < 3:
            defaults_list.append(' ')

        self.kv_pairs = {
            'item': self.item,
            'item_uid': self.item.uid,
            'item_name': self.item.name,
            'item_group_uid': self.item.group.uid,
            'item_group_name': self.item.group.name,
            'item_default_0': defaults_list[0] if defaults_list[0] else 'N',
            'item_default_1': defaults_list[1] if defaults_list[1] else 'N',
            'item_default_2': defaults_list[2] if defaults_list[2] else 'N',
            'item_note': self.item.note,
        }


class LocationMap:
    """Third tab layout; allows editing of item-location mappings"""

    def __init__(self, item: GroceryItem, store: Store):
        self.item = item
        self.store = store

        self.kv_pairs = {
            'item_name': self.item.name,
            'item_uid': self.item.uid,
            'location_name': self.location.name,
            'location_uid': self.location.uid,
        }

    @property
    def location(self):
        loc_uid = self.store[self.item.uid]
        return self.store.locations[loc_uid]


class LocationDetail:
    """Fourth tab layout; allows editing of location names and sort order"""

    def __init__(self, store: Store):
        self.store = store

    @property
    def locations(self):
        return [loc for loc in self.store.locations.values()]

    @property
    def kv_pairs(self):

        return [{'location_name': location.name,
                 'location_uid': luid} for luid, location in self.store.locations.items()]



db = Database(item_db='data/username/username.yaml')

group_details = [GroupDetail(group).kv_pairs for group in db.groups.values()]
item_details = [ItemDetail(item).kv_pairs for item in db.items.values()]
loc_maps = [([LocationMap(item, store).kv_pairs], store) for item in db.items.values() for store in db.stores.values()]
loc_details = [([LocationDetail(store).kv_pairs], store) for store in db.stores.values()]




