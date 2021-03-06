from kivy.factory import Factory
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivymd.app import MDApp

from access_app.access_dialogs import MappingAttemptedNewItem
from access_app.access_misc_widgets import AccessRecycleView
from access_app.bases import DataGenerator, LayoutContainer


class LocationMapLogic(BoxLayout):
    """Methods bound to widgets that interact with the `LocationMapRow`"""

    @staticmethod
    def create_new():
        """There's no way to add a new mapping; only modify existing ones."""

        Factory.MappingAttemptedNewItem().open()
        return True


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
            'location_names': self.spinner_values,
            'location_uid': self.location.uid_short,
        }
        return kv_pairs

    @property
    def spinner_values(self):
        locs = sorted((loc for loc in self.store.locations.values()), key=lambda x: x.uid)
        return [loc.name for loc in locs]
        # except AttributeError:
        #     return []


class LocationMapRow(LocationMapLogic):
    """View class for `RecycleView`"""

    item_name = StringProperty()
    item_uid = StringProperty()
    location_name = StringProperty()
    location_names = ListProperty()
    location_uid = StringProperty()
    store = ObjectProperty()


class LocationMapHeader(BoxLayout):
    """Labels for fields displayed in tab"""

    container = ObjectProperty()

    def __init__(self, container=None, **kwargs):
        self.container = container
        super().__init__(**kwargs)


class StoreItemMapContainer(LayoutContainer):
    """The container which holds instances of `LocationMapRow`"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def generate_data(self, elements):
        view_layouts = MDApp.get_running_app().data_factory.get('map_locations', elements)
        self.data = sorted(view_layouts, key=lambda x: x.get('item_uid'))

    def to_layout(self):
        self.container_display = AccessRecycleView(self.data, viewclass=LocationMapRow, size_hint=(1, 1))
        MDApp.get_running_app().rv_refs.append(self.container_display)


class ItemLocationContent(BoxLayout):
    """Builds the content of this tabbed panel (2).
    Content is another tabbed panel, whose tabs contain `RecycleView` instances.
    """

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.children[0]
        for name, store in app.db.stores.items():
            if name == 'default':  # Duplicated store
                default_store = store.name
                continue

            store_panel = TabbedPanelItem(text=name.capitalize())
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('map_locations', store)
            container.store = store

            items = set()
            for location in store.locations.values():
                for item in location.items:
                    if item:
                        item = app.db.items[item]
                        items.add((store, location, item))
            # print(len(items))

            container.generate_data(items)
            container.to_layout()
            store_panel.content = BoxLayout(orientation='vertical')
            store_panel.content.add_widget(LocationMapHeader(container=container))
            store_panel.content.add_widget(container.container_display)

        for panel in sub_panel.tab_list:
            # noinspection PyUnboundLocalVariable
            if panel.text == default_store:
                sub_panel.default_tab = panel
        sub_panel.tab_width = MDApp.get_running_app().root.width / (len(app.db.stores) - 1)
