class Basket:
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


class Store:
    """Maps item uids to locations in store"""

    default = None

    def __init__(self, name, mapping, basket=None):

        self.name = name
        self.locations = {}
        self.item_names = {}
        self.specials = {}
        self.location_names = {}

        for item_uid, item_name, location_uid, location_name, is_special in mapping:
            self.locations[item_uid] = location_uid
            self.item_names[item_uid] = item_name
            self.location_names[location_uid] = location_name
            if is_special.upper() != 'FALSE':
                self.specials[is_special] = location_uid

        self._basket = basket

    def __getitem__(self, item):
        return self.locations[item]

    @property
    def basket(self, source=None):
        """Consumer Price Index for this store; measure of store's prices"""
        if not self._basket:
            if source is None:
                source = 'data/default_basket.csv'
            self._basket = Basket(source)
        return self._basket.index


