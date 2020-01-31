import csv
import datetime


class Basket:

    baskets = set()

    def __init__(self, source):
        Basket.baskets.add(self)
        with open(source, 'r') as f:
            csv_reader = csv.DictReader(f)
            self.items = [line for line in csv_reader]

    def scrape(self, value):
        ...

    @property
    def index(self):
        return ...


class Store:
    """Maps item uids to locations in store"""

    default = None
    stores = {}

    def __init__(self, name, mapping):

        self.name = name
        self.data = {}
        self._basket = None
        with open(mapping) as f:
            reader = csv.reader(f)
            self.fields = next(reader)

            for line in reader:
                self.data[line[0]] = tuple(line[1:])

        Store.stores[self.name] = self

    def __getitem__(self, item):
        return self.data[item]

    @property
    def basket(self, source=None):
        if not self._basket:
            if source is None:
                source = 'data/default_basket.csv'
            self._basket = Basket(source)
        return self._basket.index


class ShoppingList:
    """Grocery List object that can be merged or formatted with store mapping data"""

    specials = ['unsorted', 'walmart', 'deli']

    def __init__(self, init_value, store='default'):

        self.items = {}  # location.uid str -> list of tuples
        self.header = {}

        self.store = Store.stores[store]

        if isinstance(init_value, dict):
            self._from_dict(init_value)
        else:
            self._from_set(init_value)

    def __hash__(self):
        return hash(self.__repr__())

    def __add__(self, other):
        """
        - Iterate through a working dict to check against values in a base dict.
        - If they match, combine into one section.
        - Preserve values that are not affected.
        """

        if len(self.items) >= other.items:
            base, working = self.items, other.items
        else:
            working, base = self.items, other.items
        half_merged = {}

        for working_outer_key, working_nested in working.items():
            half_merged_nested = {}
            try:
                base_nested = base[working_outer_key]
            except KeyError:
                half_merged[working_outer_key] = working_nested  # Just copy the section if there's no overlap
            else:
                for nested_key in working_nested:
                    if nested_key not in base_nested:
                        half_merged_nested[nested_key] = working_nested[nested_key]
                    else:
                        half_merged_nested[nested_key] = self._merge_dict_key(nested_key, working_nested, base_nested)
            half_merged[working_outer_key] = half_merged_nested

        full_merged = {**base, **half_merged}  # Copy keys from base which weren't accessed, overwrite ones that were

        return ShoppingList(full_merged)  # new object returned from addition

    @staticmethod
    def _merge_dict_key(key, first, second):
        """Add number and note values in the case of repeated items"""
        f_num, f_note = first[key]
        s_num, s_note = second[key]

        try:
            c_num = str(int(f_num) + int(s_num))
        except ValueError:
            if len(f_num) > len(s_num):
                c_num = f_num
            else:
                c_num = s_num

        if f_note and s_note:
            c_note = f'{f_note}~~{s_note}'
        else:
            c_note = f_note if f_note else s_note

        return c_num, c_note

    def _from_dict(self, init_value):
        self.items = init_value
        self.build_header()

    def _from_set(self, init_value):

        for triple in init_value:
            item, num, note = triple
            key = self.store[item.uid]

            # Location uids map to another dict containing items as keys mapping to GUI generated number and note values

            try:
                location_dict = self.items[key]
            except KeyError:
                self.items[key] = {item: (num, note)}
            else:
                location_dict[item] = (num, note)
                self.items[key] = location_dict
        self.build_header()

    def _build_header(self, needed_in_header):

        unsorted, walmart, deli = needed_in_header

        print("Needed In header:", unsorted, walmart, deli)

        keys = (len(unsorted[1]) if unsorted[1] else None,
                True if walmart[1] else False,
                True if deli[1] else False)

        header = {**{'date': self.get_date()}, **{k: v for k, v in zip(self.specials, keys)}}

        return header

    def build_header(self):
        needed = []
        do_build = False
        for key in self.specials:
            try:
                nested = self.items[key]
            except KeyError:
                needed.append((key, []))
            else:
                needed.append((key, nested))
                do_build = True

        if do_build:
            self.header = self._build_header(needed)
        else:
            self.header = {'date': self.get_date()}

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]
