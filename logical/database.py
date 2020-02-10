import datetime
import os
import time
import socket

import yaml

from logical.items import DisplayGroup, GroceryItem
from logical.stores import Store, Location
from logical.pools_and_lists import ItemPool


class Database:
    """Handles parsing database files and creating python objects"""

    groups = {}
    items = {}
    new_items = {}
    stores = {'default': None}

    def __init__(self, item_db=None, syntax=None, from_file=None, fullpath=None):

        if item_db:
            self.filepath = item_db
            self.path, self.filename = item_db.rsplit('/', maxsplit=1)
            self.username, self.ext = self.filename.split('.')
        self.file_object = from_file
        self.fullpath = fullpath

        if not syntax:
            self._setup()
            self._load_items_yaml(from_file=from_file)
        elif syntax == 'net':
            self._load_network_file()
        # TODO: elif 'other_syntaxes?':

    def __getitem__(self, item):
        """Get a reference to any stored object by its UID"""
        for d in (self.new_items, self.groups, self.items, self.stores):
            try:
                return d[item]
            except KeyError:
                pass
        else:
            raise KeyError(f'No database key present for {item}')

    # noinspection PyTypeChecker
    def _setup(self, mobile=False):
        content_root = 'data' if not self.fullpath else self.fullpath

        with open(os.path.join(content_root, 'groups.txt')) as f:
            for i, line in enumerate(f):
                if line:
                    _grp = DisplayGroup(line[:-1], uid=i)
                    self.groups[_grp.uid] = _grp

        for root, dirs, filenames in os.walk(os.path.join(content_root, 'stores')):
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
                    store = Store(name, loc_pool)
                    self.stores[name] = store

            # noinspection PyUnboundLocalVariable
            self.stores['default'] = self.stores['shoppers']

    def _load_items_yaml(self, from_file=None):
        def _do_load(file_object):
            for entries_list in yaml.load_all(file_object, Loader=yaml.Loader):
                for entry in entries_list:
                    for name, kwargs in entry.items():
                        _item = GroceryItem(name, **kwargs)
                        self.items[_item.uid] = _item

        if not from_file:
            self.file_object = open(self.filepath)
            _do_load(self.file_object)
            self.file_object.close()
        else:
            _do_load(self.file_object)

    def _load_network_file(self):
        self.file_object = self.filepath
        self._setup(mobile=True)
        self._load_items_yaml(from_file=True)

    def add_new_item(self, info: dict):
        """Method for creating a new item from dialogs or loading unknown item from pool"""
        name = info['name']
        kwargs = {k: v for k, v in info.items() if k != 'name'}
        item = GroceryItem(name, **kwargs)
        self.new_items[item.uid] = item
        return item

    @staticmethod
    def get_date():
        date, dtime = str(datetime.datetime.now()).split(" ")
        y, m, d = date.split('-')
        hour, minute, _ = dtime.split(':')
        return f'{y}.{m}.{d}.{hour}.{minute}.'

    def set_new_defaults(self, pool: ItemPool):
        """Update default options and note text based on a newly created list"""
        now = round(time.time())
        for key, triple in pool.items():
            _, new_num, new_note = triple
            item = self[key]
            defaults = [num for _time, num in item.defaults]

            try:
                new_num = int(new_num)
            except ValueError:
                new_num = ''

            if new_num in defaults:
                item.defaults.pop(defaults.index(new_num))
            elif len(defaults) >= 3:
                item.defaults = defaults[1:]

            item.defaults.append((now, new_num))

            if new_note:
                item.note = new_note

    def _dump_yaml(self, f):
        all_items = list(self.items.values()) + list(self.new_items.values())
        for item in all_items:
            name = item.name
            uid = item.uid
            group = item.group.uid
            defaults = [[float(u), v] for u, v in item.defaults]
            note = item.note

            data = [{name: {'group': group,
                            'defaults': defaults,
                            'note': note,
                            'uid': uid,
                            }
                     }]

            yaml.dump(data, f)

    def dump_local(self):
        abs_path = os.path.join(os.getcwd(), self.path)
        filename = f'{self.get_date()}{self.username}.{self.ext}'
        old_db_dir = os.path.join(abs_path, 'old_database')
        new_filepath = os.path.join(old_db_dir, filename)
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
