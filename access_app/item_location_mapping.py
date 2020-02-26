from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivymd.app import MDApp

from access_app.access_misc_widgets import AccessRecycleView
from access_app.bases import DataGenerator, LayoutContainer


class LocationMapLogic(BoxLayout):
    """"""


class LocationMapRow(DataGenerator, LocationMapLogic):
    """A row representing a single `GroceryItem` paired to its `Location` in a given `Store`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Factory must yield data rather than actual objects to be compatible with a `RecycleView`.
    """

    def __init__(self, *args, **kwargs):
        self.store = args[1]
        super().__init__(args[0], **kwargs)

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


class StoreItemMapContainer(LayoutContainer):
    """The container which holds instances of `LocationMapRow`"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def generate_data(self, elements):
        view_layouts = MDApp.get_running_app().data_factory.get('location_details', elements)
        self.data = sorted(view_layouts, key=lambda x: x.get('item_uid'))

    def to_layout(self):
        self.container_display = AccessRecycleView(self.data, viewclass=LocationMapRow)


class ItemLocationContent(BoxLayout):
    """Builds the content of this tabbed panel (2).
    Content is another tabbed panel, whose tabs contain `RecycleView` instances.
    """

    item_name = StringProperty()
    item_uid = StringProperty()
    location_name = StringProperty()
    location_uid = StringProperty()

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.children[0]
        for store in app.db.stores.values():
            if store.name == 'default':  # Duplicated store
                continue

            store_panel = TabbedPanelItem()
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('location_details', store)

            items = set()
            for location in store.locations.values():
                for item in location.items:
                    items.add(item)

            container.generate_data(items)
            container.to_layout()
            store_panel.content = container.container_display

