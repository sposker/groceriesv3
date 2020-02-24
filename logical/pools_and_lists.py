from operator import itemgetter

from logical.stores import Store


class ItemPool:
    """Pool of items wanted for a grocery list; unsorted, but may be loaded and/or merged with other pools"""

    def __init__(self, item_pool):
        self._items = {}

        for item, amount, note in item_pool:
            try:
                amount = int(amount)
            except (ValueError, TypeError):
                amount = '\u00B7'
            self._items[item.uid] = item, amount, note

    def __getitem__(self, item):
        return self._items[item]

    def __len__(self):
        return len(self._items)

    def __add__(self, other):
        """Merge keys that exist in both dicts by iterating through items in `self`, then create a new dict
         by merging into a copy of the dict `other`.

         This results in the following effects:
         - Values not present in `other` are added as new entries.
         - Values not present in `self` are preserved.
         - Values present in both `self` and `other` are merged.
         """
        if other is None:
            return self

        half_merged = {}
        for key, value0 in self.items():
            try:
                value1 = other[key]
            except KeyError:
                half_merged[key] = value0
            else:
                item, amount0, note0 = value0
                _, amount1, note1 = value1

                if not amount0 or not amount1:
                    amount2 = amount0 if amount0 else amount1
                else:
                    try:
                        amount2 = amount0 + amount1
                    except TypeError:
                        amount2 = f'{amount0} + {amount1}'

                if not note0 or not note1:
                    note2 = note0 if note0 else note1
                else:
                    note2 = f'{note0} + {note1}'
                half_merged[key] = (item, amount2, note2)

        full_merged = {**other.items_dict, **half_merged}  # Concise syntax for copying as described in docstring
        return ItemPool(full_merged.values())

    def items(self):
        return self._items.items()

    @property
    def items_dict(self):
        return self._items


class ListWriter:
    """Combine an unsorted pool of items with mapping from a given store to produce a sorted, readable list"""

    def __init__(self, pool: ItemPool, store: Store):

        self.store = store
        self.subject = self.header = self.body = self.abs_path = None

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
        for loc in sorted(self.store.specials):
            try:
                nested = self.items[loc.uid]
            except KeyError:
                needed.append(0)
            else:
                needed.append(len(nested))
                do_build = True

        self.subject = f"{self.store.name} grocery list: {self.get_date()}"
        self.header = f"Grocery List: {self.get_date()} ({self.store.name})\n"

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

    def format_plaintext(self):
        """Convert a grouped-- but not yet sorted-- set of items into a list for humans to read"""

        s = sorted([loc for loc in self.items])

        self.body = ''
        for location_uid in s:
            location = self.store.locations[location_uid]
            location_name = location.name

            self.body += f'\n{location_name.capitalize()}:\n'  # No spaces for locations
            section = sorted(list(self.items[location_uid]), key=itemgetter(0))  # Alphabetized

            for triple in section:
                item, amount, note = triple
                item_line = f'  {item.name}'  # Two spaces for items, amount on same line
                try:
                    item_line += f': {int(amount)}'
                except (TypeError, ValueError):
                    pass
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
        return f'{self.header}' f'{self.body}'

    @staticmethod
    def get_date():
        from logical.io_manager import IOManager
        return IOManager.get_date(3)[:-1]
