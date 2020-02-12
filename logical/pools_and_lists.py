import datetime
import os
import time
from operator import itemgetter

import yaml
from kivymd.app import MDApp

from logical.stores import Store


class ItemPool:
    """Pool of items wanted for a grocery list; unsorted, but may be loaded and/or merged with other pools"""

    def __init__(self, item_pool):
        self._items = {}

        for item, amount, note in item_pool:
            try:
                amount = int(amount)
            except (ValueError, TypeError):
                amount = ''
            self._items[item.uid] = item.name, amount, note

    def __getitem__(self, item):
        return self._items[item]

    def __add__(self, other):
        """Merge keys that exist in both dicts by iterating through items in `self`, then create a new dict
         by merging into a copy of the dict `other`.

         This results in the following effects:
         - Values not present in `other` are added as new entries.
         - Values not present in `self` are preserved.
         - Values present in both `self` and `other` are merged.
         """
        half_merged = {}
        for key, value0 in self.items():
            try:
                value1 = other[key]
            except KeyError:
                pass
            else:
                item, amount0, note0 = value0
                _, amount1, note1 = value1

                if not amount0 or not amount1:
                    amount2 = amount0 or amount1
                else:
                    try:
                        amount2 = amount0 + amount1
                    except TypeError:
                        amount2 = f'{amount0} + {amount1}'

                if not note0 or not note1:
                    note2 = note0 or note1
                else:
                    note2 = f'{note0} + {note1}'

                half_merged[key] = (item, amount2, note2)

        return {**other, **half_merged}  # Concise syntax for copying as described in docstring

    def items(self):
        return self._items.items()

    @staticmethod
    def get_date():
        """Generate today's date in a path-friendly format"""

        dashes = str(datetime.datetime.now()).split(" ")[0]
        y, m, d = dashes.split('-')
        return f'{y}.{m}.{d}.'

    @classmethod
    def from_file(cls, path):
        """Create an ItemPool object by loading data from file
        Lines in files should have the following format:
        `item_uid` OR `item.name`: [`amount`, `note`]
        Item object will be looked up via DB, if not found it is a new/unsorted item and created
        """

        db = MDApp.get_running_app().db
        pool = set()
        now = time.time()
        with open(path) as doc:
            for base_dict in yaml.load_all(doc, Loader=yaml.Loader):
                for uid, info in base_dict.items():
                    try:
                        item = db.items[uid]
                    except KeyError:  # New item created during previous program run
                        amount, note = info
                        name, group = uid.split(';')
                        kwargs = {'name': name, 'group': group, 'defaults': [(now, amount)], 'note': note}
                        item = db.add_new_item(kwargs)
                    else:
                        amount, note = info
                    pool.add((item, amount, note))

        return cls(pool)

    def dump_yaml(self, filename=None):
        """Save ItemPool to text format"""
        db = MDApp.get_running_app().db
        dump_dict = {}
        for key, value in self._items.items():
            name, amount, note = value
            if key not in db.items:
                item = db.new_items[key]
                key = f'{name};{item.group.uid}'
            dump_dict[key] = [amount, note]

        if not filename:
            filename = os.path.join('data\\username\\pools', self.get_date() + 'itempool.yaml')

        with open(filename, 'w') as f:
            yaml.dump(dump_dict, f)


class ShoppingList:
    """Formatted list for a given store"""

    def __init__(self, pool: ItemPool, store: Store, path: str):

        self.store = store
        self.path = path
        self.subject = self.header = self.body = None

        self.items = {}
        for uid, triple in pool.items():  # item, num, note = triple

            try:
                location_key = self.store[uid]
            except KeyError as e:
                location_key = 'l00'  # unsorted item
            try:
                loc_pool = self.items[location_key]
            except KeyError:
                loc_pool = set()
                self.items[location_key] = loc_pool
            finally:
                loc_pool.add(triple)

        self.build_header()

    def __str__(self):
        return self.content

    def build_header(self):
        """Check the special item categories, the location of which may vary by store.
        If any special categories are needed, indicate this via key-value pairs in header and email subject.
        """

        needed = []
        do_build = False
        for loc in self.store.specials:
            try:
                nested = self.items[loc]
            except KeyError:
                needed.append(0)
            else:
                needed.append(len(nested))
                do_build = True

        self.subject = f" ShoppingList {self.get_date()}"
        self.header = f"{self.get_date()}: Grocery List\n"

        if do_build:
            fstrings = [(lambda u: f"List contains {u} unsorted item(s).\n",
                         lambda u: f"UNS:{u}- "),
                        (lambda w: f"List includes {w} Wal-mart items.\n",
                         lambda u: 'WAL-'),
                        (lambda d: f"List contains {d} Deli items-- deli closes at 8pm.\n",
                         lambda _: 'DELI'),
                        ]
            self.subject += ': '
            for val, strings in zip(needed, fstrings):
                if val:
                    _head, _subj = strings
                    self.header += _head(val)
                    self.subject += _subj(val)

    @staticmethod
    def get_date():
        """Generate today's date in a path-friendly format"""

        dashes = str(datetime.datetime.now()).split(" ")[0]
        y, m, d = dashes.split('-')
        return f'{y}.{m}.{d}'

    def write(self, do_print=False):
        """Write list to text format.
        Note that email functionality belongs to the GUI which is responsible for loading the credentials file.
        """
        date = self.get_date()
        filename = date + '.ShoppingList.txt'
        abspath = os.path.join(self.path, filename)

        with open(abspath, 'w') as f:
            f.write(self.content)

        if do_print:
            os.startfile(abspath, 'print')

    def format_plaintext(self):
        """Convert an grouped-- but not yet sorted-- set of items into a list for humans to read"""

        s = sorted([loc for loc in self.items])

        self.body = ''
        for location_uid in s:
            location = self.store.locations[location_uid]
            location_name = location.name

            self.body += f'\n{location_name.capitalize()}:\n'  # No spaces for locations
            section = sorted(list(self.items[location_uid]), key=itemgetter(0))  # Alphabetized

            for triple in section:
                name, amount, note = triple
                item_line = f'  {name}'  # Two spaces for items, amount on same line
                if amount:
                    item_line += f': {amount}'
                if note:
                    item_line += f'\n    -{note}'  # Four spaces for notes
                item_line += '\n'
                self.body += item_line

    @property
    def email_content(self):
        """Avoid storing the same content twice"""
        return f'Subject: {self.subject}\n\n' + self.content

    @property
    def content(self):
        return f'{self.header}{self.body}'
