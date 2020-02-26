from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivymd.app import MDApp

from access_app.access_misc_widgets import AccessRecycleView
from access_app.bases import DataGenerator, LayoutContainer


class LocationMapLogic(BoxLayout):
    """"""


class LocationMapData(DataGenerator):
    """This class translates a `GroceryItem`-`Location` pair into a dict representation.
    Factory must yield data rather than actual objects to be compatible with a `RecycleView`.
    """

    def __init__(self, args, **kwargs):
        self.store, self.location, element = args
        super().__init__(element, **kwargs)

    @property
    def kv_pairs(self):
        kv_pairs = {
            'store': self.store,
            'item_name': self.element.name,
            'item_uid': self.element.uid,
            'location_name': self.location.name,
            'location_uid': self.location.uid,
        }
        return kv_pairs


class LocationMapRow(LocationMapLogic):
    """View class for `RecycleView`"""

    item_name = StringProperty()
    item_uid = StringProperty()
    location_name = StringProperty()
    location_uid = StringProperty()
    store = ObjectProperty()

    @property
    def location_names(self):
        try:
            return [loc.name for loc in self.store.locations.values()]
        except AttributeError:
            return []


class StoreItemMapContainer(LayoutContainer):
    """The container which holds instances of `LocationMapRow`"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def generate_data(self, elements):
        view_layouts = MDApp.get_running_app().data_factory.get('map_locations', elements)
        self.data = sorted(view_layouts, key=lambda x: x.get('item_uid'))

    def to_layout(self):
        self.container_display = AccessRecycleView(self.data, viewclass=LocationMapRow, size_hint=(1,1))


class ItemLocationContent(BoxLayout):
    """Builds the content of this tabbed panel (2).
    Content is another tabbed panel, whose tabs contain `RecycleView` instances.
    """

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.children[0]
        for name, store in app.db.stores.items():
            if name == 'default':  # Duplicated store
                continue

            store_panel = TabbedPanelItem(text=name.capitalize())
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('map_locations', store)
            container.store = store

            items = set()
            for location in store.locations.values():
                for item in location.items:
                    if item:
                        item = app.db.items[item]  # TODO
                        """Need to find a clean way to pass store instance along with items for creation
                        ALSO need it to work with factory
                        """
                        items.add((store, location, item))
            # print(len(items))

            container.generate_data(items)
            container.to_layout()
            store_panel.content = container.container_display
        # noinspection PyUnboundLocalVariable
        sub_panel.default_tab = store_panel
        sub_panel.tab_width = MDApp.get_running_app().root.width/(len(app.db.stores) - 1)
