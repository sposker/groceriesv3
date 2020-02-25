from abc import ABC, abstractmethod


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


class GroupDetail(ViewElementLayout):
    """First tab view-class; allows editing of group names and sort order"""

    @property
    def kv_pairs(self):
        kv_pairs = {
            'group_name': self.element.name,
            'group_uid': self.element.uid,
        }
        return kv_pairs


class ItemDetail(ViewElementLayout):
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


class LocationMap(ViewElementLayout):
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


class LocationDetail(ViewElementLayout):
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


class ObjectProcessor:
    """The implementation of ObjectProcessor is completely generic, and it only requires a conversion-friendly
     `object_` and a `format` as parameters.

    The `format` is used to identify the concrete implementation of the `LayoutContainer` and is resolved
    by the `self.factory` object. The `object_` parameter refers to another abstract interface that should be
    implemented on any object type you want to convert into a layout representation.
    """

    factory = None

    def convert(self, object_, format_):
        container = self.factory.get(format_)
        object_.generate_fields(container)
        return container.to_layout



