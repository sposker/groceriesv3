
from abc import ABC, abstractmethod

from kivy.uix.boxlayout import BoxLayout

from access_app.access_misc_widgets import AccessRecycleView
# from access_app.view_classes import GroupDetail, ItemDetail, LocationMap, LocationDetail


class LayoutContainer(ABC):
    """Containers holding various representations of elements"""

    layout = None

    def __init__(self):
        self.data = []
        self.display = None

    @abstractmethod
    def to_layout(self):
        raise NotImplementedError


class GroupDetailContainer(LayoutContainer):
    """First tab layout; allows editing of group names and sort order"""

    def to_layout(self):
        self.display = BoxLayout(
            orientation='vertical',
            spacing=8,
        )

        for row in self.data:
            new_row = self.layout(row)
            self.display.add_widget(new_row)


class ItemDetailContainer(LayoutContainer):
    """Second tab layout; allows editing of item details."""

    def to_layout(self):
        self.display = AccessRecycleView(self.data, viewclass=self.layout)


class StoreItemMapContainer(LayoutContainer):
    """Third tab layout; allows editing of item-location mappings"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def to_layout(self):
        self.display = AccessRecycleView(self.data, viewclass=self.layout)


class StoreLocationDetailContainer(LayoutContainer):
    """Fourth tab layout; allows editing of location names and sort order"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def to_layout(self):
        self.display = BoxLayout(
            orientation='vertical',
            spacing=8,
        )

        for row in self.data:
            new_row = self.layout(row)
            self.display.add_widget(new_row)


class ContainerFactory:

    def __init__(self, **kwargs):
        self._creators = kwargs

    def register(self, name, container):
        self._creators[name] = container

    def get_container(self, format_, *args):
        container_cls, view_cls = self._creators[format_]
        container_cls.layout = view_cls
        return container_cls(*args)
