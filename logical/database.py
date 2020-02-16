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

    def __init__(self, item_db=None, syntax=None, from_file=None):

        if item_db:
            self.filepath = item_db
            self.path, self.filename = item_db.rsplit('/', maxsplit=1)
            self.username, self.ext = self.filename.split('.')
        self.content_root = 'data'
        self.file_object = from_file
        self._store_default = 'shoppers'

        if not syntax:
            self.build()
            self._build_items(from_file=from_file)
        elif syntax == 'net':
            self._load_network_file()
        # TODO: elif 'other_syntaxes?':

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
    def build(self, mobile=False):
        """Create various python objects for use in app"""
        self._build_groups()
        self._build_stores()
        self._build_items()

    def _build_groups(self):
        """Build `DisplayGroup` objects from data source"""

        with open(os.path.join(self.content_root, 'groups.txt')) as f:
            for i, line in enumerate(f):
                if line:
                    group_ = DisplayGroup(line[:-1], uid=i)
                    self.groups[group_.uid] = group_

    def _build_stores(self):
        """Build `Store` objects from data source"""
        for root, dirs, filenames in os.walk(os.path.join(self.content_root, 'stores')):
            for filename in filenames:
                name, ext = filename.split('.')
                with open(os.path.join(root, filename)) as file:
                    loc_pool = set()
                    for loc_name, values in yaml.load(file, Loader=yaml.Loader).items():
                        uid = values['_uid']
                        special = values['_special']
                        item_pool = set(values['items'])
                        loc = Location(loc_name, items=item_pool, uid=uid, special=special)
                        loc_pool.add(loc)

                    self.stores[name] = Store(name, loc_pool)

            self.stores['default'] = self.stores[self._store_default]

    def _build_items(self, from_file=None):
        """Build `GroceryItem` objects from data source"""

        def load_helper(file_object):
            for uid, kwargs in yaml.load(file_object, Loader=yaml.Loader).items():
                item = GroceryItem(uid=uid, **kwargs)
                self.items[item.uid] = item

        if not from_file:
            with open(self.filepath) as self.file_object:
                load_helper(self.file_object)
        else:
            load_helper(self.file_object)

    @property
    def items_by_group(self):
        by_group = {}
        for item in self.items.values():
            try:
                by_group[item.group].append(item)
            except KeyError:
                by_group[item.group] = [item]
        return by_group

    def _load_network_file(self):
        self.file_object = self.filepath
        self.build(mobile=True)
        self._build_items(from_file=True)

    def add_new_item(self, info: dict):
        """Method for creating a new item from dialogs or loading unknown item from pool"""
        name = info['name']
        kwargs = {k: v for k, v in info.items() if k != 'name'}
        item = GroceryItem(name, **kwargs)
        self.new_items[item.uid] = item
        return item

    @staticmethod
    def get_date():
        date_, time_ = str(datetime.datetime.now()).split(" ")
        y, m, d = date_.split('-')
        hour, minute, _ = time_.split(':')
        return f'{y}.{m}.{d}.{hour}.{minute}.'

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

    def _dump_yaml(self, f):
        all_items = list(self.items.values()) + list(self.new_items.values())
        data = {}

        for item in all_items:
            name = item.name
            uid = item.uid
            group = item.group.uid

            new_defaults = []
            for time_, amount_ in item.defaults:
                try:
                    amount_ = int(amount_)
                except (ValueError, TypeError):
                    amount_ = None
                new_defaults.append([int(round(time_)), amount_])

            note = item.note

            data[uid] = {'group': group,
                         'defaults': new_defaults,
                         'note': note,
                         'name': name,
                         }

        yaml.dump(data, f)

    def dump_local(self):
        abs_path = os.path.join(os.getcwd(), self.path)
        filename = f'{self.get_date()}{self.username}.{self.ext}'
        db_copy_destination = os.path.join(abs_path, 'old_database')
        new_filepath = os.path.join(db_copy_destination, filename)
        os.rename(self.filepath, new_filepath)

        with open(self.filepath, 'w') as f:
            self._dump_yaml(f)

    def dump_mobile(self, pair):
        # TODO: check whether socketserver is availible

        s = socket.socket()
        s.connect(pair)

        with s.makefile(mode='w') as f:
            self._dump_yaml(f)

        s.close()

    def _load_picker(self):
        pass
