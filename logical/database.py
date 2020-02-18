import datetime
import os
import socket
import time

import yaml

from logical.groups_and_items import DisplayGroup, GroceryItem
from logical.pools_and_lists import ItemPool
from logical.stores import Store, Location


class Database:
    """Handles parsing database files and creating python objects"""

    groups = {}
    items = {}
    new_items = {}
    stores = {}

    def __init__(self, **kwargs):

        try:
            self._store_default = kwargs.get('default_store')
        except KeyError:
            self._store_default = None

        try:
            if not kwargs.get('build_empty'):
                self.build(**kwargs)
        except KeyError:
            self.build(**kwargs)

    def __getitem__(self, item):
        """Get a reference to any stored object by its UID"""
        for dict_ in (self.groups, self.items, self.stores, self.new_items,):
            try:
                return dict_[item]
            except KeyError:
                pass
        else:
            raise KeyError(f'No database key present in set(items, groups, stores, new_items) for {item}')

    # noinspection PyTypeChecker
    def build(self, **kwargs):
        """Create various python objects for use in app"""
        self.build_groups(kwargs.get('groups'))
        self.build_stores(kwargs.get('stores'))
        self.build_items(kwargs.get('items'))

    def build_groups(self, source):
        """Build `DisplayGroup` objects from data source"""

        for i, line in enumerate(source):
            if line:
                group_ = DisplayGroup(line, uid=i)
                self.groups[group_.uid] = group_

    def build_stores(self, source):
        """Build `Store` objects from data source"""

        for name, data in source.items():
            loc_pool = set()

            for loc_name, values in data.items():
                uid = values['_uid']
                special = values['_special']
                item_pool = set(values['items'])
                loc = Location(loc_name, items=item_pool, uid=uid, special=special)
                loc_pool.add(loc)

            self.stores[name] = Store(name, loc_pool)

            if self._store_default:
                self.stores['default'] = self.stores[self._store_default]

    def build_items(self, source):
        """Build `GroceryItem` objects from data source"""

        # print(source)

        for uid, kwargs in source.items():
            item = GroceryItem(uid=uid, **kwargs)
            self.items[item.uid] = item

    @property
    def items_by_group(self):
        by_group = {}
        for item in self.items.values():
            try:
                by_group[item.group].append(item)
            except KeyError:
                by_group[item.group] = [item]
        return by_group

    def add_new_item(self, info: dict):
        """Method for creating a new item from dialogs or loading unknown item from pool"""
        name = info['name']
        kwargs = {k: v for k, v in info.items() if k != 'name'}
        item = GroceryItem(name, **kwargs)
        self.new_items[item.uid] = item
        return item

    def set_new_defaults(self, pool: ItemPool):
        """Update default options and note text based on a newly created list"""
        now = round(time.time())
        for key, triple in pool.items():
            _, new_num, new_note = triple
            item = self[key]
            defaults_ = [amount for _, amount in sorted(item.defaults, key=lambda d: d[0])]

            try:
                new_num = int(new_num)
            except ValueError:
                new_num = "\u00B7"

            if new_num in defaults_:
                item.defaults.pop(defaults_.index(new_num))
            elif len(defaults_) >= 3:
                item.defaults = defaults_[1:]

            item.defaults.append((now, new_num))

            if new_note:
                item.note = new_note

