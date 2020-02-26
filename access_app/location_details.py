from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer


class LocationDetailLogic(BoxLayout):
    """"""


# noinspection PyRedeclaration
class LocationDetailRow(DataGenerator, LocationDetailLogic):
    """A row representing a single `Location` within a given `Store`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Factory must yield actual objects to populate a `BoxLayout`.
    """

    location_name = StringProperty()
    location_uid = StringProperty()

    def __init__(self, element, **kwargs):
        super().__init__(element, **kwargs)

    @property
    def kv_pairs(self):
        kv_pairs = {'location_name': self.element.name,
                    'location_uid': self.element.uid}
        return kv_pairs

    @property
    def location_name(self):
        return self.element.name

    @property
    def location_uid(self):
        return self.element.uid


class StoreLocationDetailContainer(LayoutContainer):
    """The container which holds instances of `LocationDetailRow`"""

    def __init__(self, store):
        self.store = store
        super().__init__()

    def generate_data(self, elements):
        app = MDApp.get_running_app()
        view_layouts = sorted(app.data_factory.get('location_details', elements), key=lambda x: x.sort_key)
        self.fill_container(view_layouts, 14)

    def to_layout(self):
        self.container_display = BoxLayout()


class ModLocationsContent(BoxLayout):
    """Builds the content of this tabbed panel (3).
    Content is another tabbed panel, whose tabs contain `BoxLayout` instances.
    """

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.children[0]
        for name, store in app.db.stores.items():
            if name == 'default':  # Duplicated store
                continue

            store_panel = TabbedPanelItem(text=name.capitalize())
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('location_details', store)
            container.store = store

            container.to_layout()
            # print(container.container_display)
            store_panel.content = BoxLayout(size_hint=(1, 1),
                                            pos_hint={'center_x': .5, 'center_y': .5},
                                            orientation='vertical',
                                            )
            store_panel.content.add_widget(container.container_display)
            container.generate_data(store.locations.values())
            # print(len(container.container_display.children))

        # noinspection PyUnboundLocalVariable
        sub_panel.default_tab = store_panel
        sub_panel.tab_width = MDApp.get_running_app().root.width / (len(app.db.stores) - 1)
