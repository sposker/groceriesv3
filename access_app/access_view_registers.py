from abc import ABC, abstractmethod

from access_app.access_view_methods import GroupDetailLogic, LocationDetailLogic, LocationMapLogic, ItemDetailLogic


class ViewElementLayout(ABC):
    """Layout for viewing relevant item information"""

    def __init__(self, element):
        self.element = element

    def generate_fields(self, container_format):
        container_format.data.append(self.kv_pairs)

    @property
    @abstractmethod
    def kv_pairs(self):
        return None

    @property
    def sort_key(self):
        return self.element.uid


class GroupDetail(ViewElementLayout, GroupDetailLogic):
    """First tab view-class; allows editing of group names and sort order"""

    @property
    def kv_pairs(self):
        kv_pairs = {
            'group_name': self.element.name,
            'group_uid': self.element.uid,
        }
        return kv_pairs


class ItemDetail(ViewElementLayout, ItemDetailLogic):
    """Second tab view-class; allows editing of item details."""


    @property
    def kv_pairs(self):
        defaults_list = sorted(self.element.defaults.copy(), key=lambda i: i[0])
        defaults_list = [str(num) for _, num in defaults_list]
        while len(defaults_list) < 3:
            defaults_list.append('')
        kv_pairs = {
            'item': self.element,
            'item_uid': self.element.uid,
            'item_name': self.element.name,
            'item_group_uid': self.element.group.uid,
            'item_group_name': self.element.group.name,
            'item_default_0': defaults_list[0],
            'item_default_1': defaults_list[1],
            'item_default_2': defaults_list[2],
            'item_note': self.element.note,
        }
        return kv_pairs


class LocationMap(ViewElementLayout, LocationMapLogic):
    """Third tab view-class; allows editing of item-location mappings"""

    def __init__(self, element, store):
        self.store = store
        super().__init__(element)

    @property
    def kv_pairs(self):
        kv_pairs = {
            'item_name': self.element.name,
            'item_uid': self.element.uid,
            'location_name': self.location.name,
            'location_uid': self.location.uid,
        }
        return kv_pairs

    @property
    def location(self):
        loc_uid = self.store[self.element.uid]
        return self.store.locations[loc_uid]


class LocationDetail(ViewElementLayout, LocationDetailLogic):
    """Fourth tab view-class; allows editing of location names and sort order"""

    def __init__(self, element, store):
        self.store = store
        super().__init__(element)

    @property
    def kv_pairs(self):
        kv_pairs = {'location_name': self.location.name,
                    'location_uid': self.location.uid}
        return kv_pairs

    @property
    def location(self):
        loc_uid = self.store[self.element.uid]
        return self.store.locations[loc_uid]


class ViewFactory:

    def __init__(self, **kwargs):
        self._creators = kwargs

    def register(self, name, container):
        self._creators[name] = container

    def get_view(self, format_, *args):
        view_cls = self._creators[format_]
        return view_cls(*args)