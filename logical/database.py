import datetime
import yaml
import time
import socket

from logical.items import DisplayGroup, GroceryItem
from logical.stores import ShoppingList


class DataBase:
    """Handles parsing database files and creating python objects"""

    groups = {}
    items = {}
    new_items = {}

    def __init__(self, item_db, syntax=None, from_file=None):
        self.filename = item_db
        self.file_object = from_file

        if not syntax:
            self._setup()
            self._load_yaml(from_file=from_file)
        elif syntax == 'net':
            self._load_network_file()
        # TODO: elif 'other_syntaxes?':

    def _setup(self, mobile=False):
        _path = 'data/groups.txt'

        with open(_path) as f:
            for i, line in enumerate(f):
                if line:
                    _grp = DisplayGroup(line[:-1], uid=i)
                    self.groups[_grp.uid] = _grp

    def _load_yaml(self, from_file=None):

        def _do_load(file_object):
            for entries_list in yaml.load_all(file_object, Loader=yaml.Loader):
                for entry in entries_list:
                    name = [key for key in entry][0]
                    kwargs = entry[name]

                    _item = GroceryItem(name, **kwargs)
                    self.items[_item.uid] = _item

        if not from_file:
            self.file_object = open(self.filename)
            _do_load(self.file_object)
            self.file_object.close()
        else:
            _do_load(self.file_object)

    def _load_network_file(self):
        self.file_object = self.filename
        self._setup(mobile=True)
        self._load_yaml(from_file=True)

    @staticmethod
    def get_date():
        date, dtime = str(datetime.datetime.now()).split(" ")
        y, m, d = date.split('-')
        hour, minute, _ = dtime.split(':')
        return f'{y}.{m}.{d}.{hour}.{minute}.'

    def set_new_defaults(self, shopping: ShoppingList):
        now = time.time()
        for item in shopping.items.values():
            for key, pair in item.items():
                _num, note = pair
                if _num:
                    num = int(_num)
                else:
                    num = _num
                try:
                    _ = self.items[key.uid]
                except KeyError:
                    continue
                else:
                    default_nums = [n for _, n in key.defaults]
                    if num in default_nums:
                        del key.defaults[default_nums.index(num)]
                        key.defaults.append((now, num))
                    else:
                        if len(key.defaults) >= 2:
                            del key.defaults[0]
                        key.defaults.append((now, num))

                    if note:
                        key.note = note

    def _dump_yaml(self, f):
        all_items = list(self.items.values()) + list(self.new_items.values())
        for item in all_items:
            name = item.name
            uid = item.uid if item.uid else ''
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

    def dump_local(self, db_path):
        import os
        new_filename = os.getcwd() + '\\dbs\\' + self.get_date() + self.filename
        os.rename(self.filename, new_filename)

        with open(db_path, 'w') as f:
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