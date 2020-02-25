"""
mapping = {
    'mod_groups': (populate_mod_group, GroupDetail, ModGroupLayout,),
    'item_details': (populate_item_details, ItemDetail, AccessRecycleView, ItemDetailsLayout,),
    'locs_map': (populate_location_mapping, LocationMap, LocsMapBase, ItemLocationLayout,),
    'mod_locs': (populate_location_details, LocationDetail, TabbedPanel, ModLocationsLayout),
    }
"""

from abc import ABC, abstractmethod

from kivy.uix.boxlayout import BoxLayout

from access_app.access_app import AccessRecycleView
# from access_app.view_classes import GroupDetail, ItemDetail, LocationMap, LocationDetail


class LayoutContainer(ABC):
    """Containers holding various representations of elements"""

    def __init__(self, layout):
        self.layout = layout
        self.data = []
        self.container = None

    @abstractmethod
    def to_layout(self):
        pass


class GroupDetailContainer(LayoutContainer):
    """First tab layout; allows editing of group names and sort order"""

    def to_layout(self):
        self.container = BoxLayout(
            orientation='vertical',
            spacing=8,
        )

        for row in self.data:
            new_row = self.layout(row)
            self.container.add_widget(new_row)


class ItemDetailContainer(LayoutContainer):
    """Second tab layout; allows editing of item details."""

    def to_layout(self):
        self.container = AccessRecycleView(self.data, viewclass=self.layout)


class StoreItemMapContainer(LayoutContainer):
    """Third tab layout; allows editing of item-location mappings"""

    def __init__(self, layout, store):
        self.store = store
        super().__init__(layout)

    def to_layout(self):
        self.container = AccessRecycleView(self.data, viewclass=self.layout)


class StoreLocationDetailContainer(LayoutContainer):
    """Fourth tab layout; allows editing of location names and sort order"""

    def __init__(self, layout, store):
        self.store = store
        super().__init__(layout)

    def to_layout(self):
        self.container = BoxLayout(
            orientation='vertical',
            spacing=8,
        )

        for row in self.data:
            new_row = self.layout(row)
            self.container.add_widget(new_row)


class ContainerFactory:

    def __init__(self, **kwargs):
        self._creators = kwargs

    def register(self, name, container):
        self._creators[name] = container

    def get(self, format_):
        return self._creators[format_]
