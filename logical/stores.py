class Basket:
    # TODO
    baskets = set()

    def __init__(self, source):
        Basket.baskets.add(self)
        with open(source, 'r') as f:
            ...

    def scrape(self, value):
        ...

    @property
    def index(self):
        return ...


class Location:
    """Location object representing a physical location or aisle inside a store"""

    def __init__(self, name, items=None, uid=None, special=False):
        self.name = name
        self.is_special = special
        self.uid = uid
        self.items = items if items else set()

    def __lt__(self, other):
        return self.uid < other.uid

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return hash(self.__repr__())

    def add_item(self, item):
        return self.items.add(item)


class Store:
    """Maps item uids to locations in store"""

    default = None

    def __init__(self, name, locations: set, basket=None):

        self.name = name
        self.locations = {}
        self.specials = set()
        self._basket = basket

        for loc in locations:
            self.locations[loc.uid] = loc
            if loc.is_special:
                self.specials.add(loc)

        if 'l00' not in self.locations:
            self.create_unsorted()

    def __getitem__(self, item):
        for location in self.locations.values():
            if item in location.items:
                return location.uid
        else:
            raise KeyError(f'Key {item} not present in {self.name} items.')

    @property
    def basket(self):
        """Consumer Price Index for this store; measure of store's prices"""
        if not self._basket:
            if ... is None:
                _ = 'data/default_basket.csv'
            ...  # TODO
        return self._basket.index

    def create_unsorted(self):
        loc = Location('Unsorted', uid='l00', special=True)
        self.specials.add(loc)
        self.locations[loc.uid] = loc


