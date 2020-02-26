from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer


class LocationDetailLogic(BoxLayout):
    """"""


class LocationDetailRow(DataGenerator, LocationDetailLogic):
    """A row representing a single `Location` within a given `Store`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Factory must yield actual objects to populate a `BoxLayout`.
    """

    def __init__(self, element, **kwargs):
        super().__init__(element, **kwargs)

    @property
    def kv_pairs(self):
        kv_pairs = {'location_name': self.location.name,
                    'location_uid': self.location.uid}
        return kv_pairs

    @property
    def location(self):
        loc_uid = self.store[self.element.uid]
        return self.store.locations[loc_uid]


class StoreLocationDetailContainer(LayoutContainer):
    """The container which holds instances of `LocationDetailRow`"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def generate_data(self, elements):
        for e in MDApp.get_running_app().data_factory.get('location_details', elements):
            print(e.element)
        view_layouts = MDApp.get_running_app().data_factory.get('location_details', elements)
        self.data = sorted(view_layouts, key=lambda x: str(x.element))

    def to_layout(self):
        self.container_display = BoxLayout(
            orientation='vertical',
            spacing=8,
        )


class ModLocationsContent(BoxLayout):
    """Builds the content of this tabbed panel (3).
    Content is another tabbed panel, whose tabs contain `BoxLayout` instances.
    """

    location_name = StringProperty()
    location_uid = StringProperty()

    pairs = {}

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.children[0]
        for store in app.db.stores.values():
            if store.name == 'default':  # Duplicated store
                continue

            store_panel = TabbedPanelItem()
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('location_details', store)

            container.to_layout()
            container.generate_data(store.locations.values())
            store_panel.content = container.container_display

