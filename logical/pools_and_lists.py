import datetime
import time
import os
from operator import itemgetter

from kivymd.app import MDApp

import yaml

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
        print(path)
        db = MDApp.get_running_app().db
        pool = set()
        now = time.time()
        with open(path) as doc:
            print(f'opened {path}')
            for base_dict in yaml.load_all(doc, Loader=yaml.Loader):
                for uid, info in base_dict.items():
                    try:
                        item = db.items[uid]
                    except KeyError:  # New item created during previous program run
                        amount, note = info
                        kwargs = {'name': uid, 'defaults': (amount, now), 'note': note}
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
                key = name
            dump_dict[key] = [amount, note]

        if not filename:
            filename = os.path.join('data\\username\\pools', self.get_date() + 'itempool.yaml')

        with open(filename, 'w') as f:
            yaml.dump(dump_dict, f)


class ShoppingList:
    """Formatted list for a given store"""

    def __init__(self, pool: ItemPool, store: Store):

        self.store = store
        self.header = self._email_content = self.content = None

        by_location = {}
        for uid, triple in pool.items():
            item, num, note = triple

            try:
                location_key = self.store[uid]
            except KeyError:
                location_key = 'l00'  # unsorted item

            try:
                location_dict = by_location[location_key]
            except KeyError:
                by_location[location_key] = {item: (num, note)}
            else:
                location_dict[item] = (num, note)
                by_location[location_key] = location_dict

        self.build_header(by_location)
        self.items = by_location

    def build_header(self, items_by_location: dict):
        """Check the special item categories, the location of which may vary by store.
        If any special categories are needed, indicate this via key-value pairs in header.
        """

        needed = []
        do_build = False
        for loc_name, loc_uid in self.store.specials.items():
            try:
                nested = items_by_location[loc_uid]
            except KeyError:
                needed.append((loc_uid, None, 0))
            else:
                needed.append((loc_uid, loc_name, len(nested)))
                do_build = True

        self.header = {'date': self.get_date()}
        if do_build:
            while needed:
                _, loc_name, num = needed.pop()
                self.header[loc_name] = num

    @staticmethod
    def get_date():
        """Generate today's date in a path-friendly format"""

        dashes = str(datetime.datetime.now()).split(" ")[0]
        y, m, d = dashes.split('-')
        return f'{y}.{m}.{d}.'

    def write(self, do_print=False):
        """Write list to text format.
        Note that email functionality belongs to the GUI which is responsible for loading the credentials file.
        """
        date = self.get_date()
        filename = date + 'ShoppingList'
        path = os.getcwd()
        abspath = f"{path}\\data\\lists\\{filename}.txt"

        with open(abspath, 'w') as f:
            f.write(self.content)

        if do_print:
            os.startfile(abspath, 'print')

    def format_plaintext(self):
        """Convert an organized set of items into a list for humans to read"""

        subject = f" ShoppingList {self.header['date']}"
        header = f"{self.header['date']}: Grocery List\n"
        if len(self.header) != 1:
            subject += ': '

            if u := self.header['unsorted']:
                header += f"List contains {u} unsorted item(s).\n"
                subject += f"UNS:{u}- "
            if w := self.header['walmart']:
                header += f"List includes {w} Wal-mart items.\n"
                subject += 'WAL-'
            if h := self.header['deli']:
                header += f"List contains {h} Deli items-- deli closes at 8pm.\n"
                subject += 'DELI'

        # convert the dict mapping `location_uid` to `nested: dictionary` into list of tuples, then sort it
        s = sorted([(k, v) for k, v in self.items.items()], key=itemgetter(0))

        body = ''
        for location_uid, nested in s:
            location_name = self.store.location_names[location_uid]
            body += f'\n{location_name.capitalize()}:\n'  # No spaces for locations
            for item, pair in nested.items():
                location_name = item.name
                num, note = pair
                item_line = f'  {location_name}'  # Two spaces for items, amount on same line
                if num:
                    item_line += f': {num}'
                if note:
                    item_line += f'\n    -{note}'  # Four spaces for notes
                item_line += '\n'
                body += item_line

        self._email_content = f'Subject: {subject}\n\n'
        self.content = f'{header}{body}'

    @property
    def email_content(self):
        """Avoid storing the same content twice"""
        return self._email_content + self.content
