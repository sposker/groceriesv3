from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer
from logical.stores import Location


class LocationDetailLogic:
    """Methods bound to widgets that interact with the `LocationDetailRow`"""

    element = None

    def create_new(self):
        """Add a new Location to our store via factory"""
        store = self._find_store(self.element.uid)
        uid_index = max(int(uid[-2:]) for uid in store.locations)
        new_uid = store.uid + 'l' + str(uid_index + 1).zfill(2)
        loc = Location('New Location', uid=new_uid)
        store.locations[loc.uid] = loc
        self.refresh_from_data(store)
        return True  # Prevents repeating creation for each tab

    @staticmethod
    def _find_store(uid):
        for store_ in MDApp.get_running_app().db.stores.values():
            if uid in store_.locations:
                return store_

    def shift(self, direction):
        """Attempt to change a `Location`'s uid."""

        uid = self.element.uid
        store = self._find_store(uid)
        z_factor = 2
        index = int(uid[-2:])

        try:
            other_location = store.locations[store.uid + 'l' + str(index + direction).zfill(z_factor)]
        except KeyError:
            return  # Invalid selection, usually first or last item
        else:
            other_location.uid = self.element.uid
            self.element.uid = store.uid + 'l' + str(index + direction).zfill(z_factor)
            store.locations.update({self.element.uid: self.element, other_location.uid: other_location})
            return store  # Successfully swapped location uids (and therefore sort order)

    def swap(self, value):
        """Initiate swapping values between two groups."""
        result = self.shift(value)
        if result:
            self.refresh_from_data(result)

    def refresh_from_data(self, store):
        """Method is unique in each base class"""
        rows = 14
        lower_grid = self.parent.parent
        app = MDApp.get_running_app()
        view_layouts = sorted(app.data_factory.get('location_details', store.locations.values()),
                              key=lambda x: x.sort_key)
        lower_grid.clear_widgets()

        # TODO: This is repeated code from LayoutContainer(ABC).fill_container(self, layouts, rows)
        # TODO: Find a clean way to refactor this part

        sections = []
        while view_layouts:
            sections.append(view_layouts[:rows])
            view_layouts = view_layouts[rows:]
        else:
            while len(sections[-1]) < rows:
                sections[-1].append(Widget())

        for widgets_list in sections:
            child = BoxLayout(orientation='vertical', spacing=8)
            lower_grid.add_widget(child)
            for w in widgets_list:
                child.add_widget(w)
                w.size_hint = (1, 1)


# noinspection PyRedeclaration,PyAbstractClass
class LocationDetailRow(DataGenerator, LocationDetailLogic):
    """A row representing a single `Location` within a given `Store`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Factory must yield actual objects to populate a `BoxLayout`.
    """

    # location_name = StringProperty()
    # location_uid = StringProperty()

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
        return self.element.uid_short


class LocationDetailHeader(BoxLayout):
    """Labels for fields displayed in tabs"""


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
                default_store = store.name
                continue

            store_panel = TabbedPanelItem(text=name.capitalize())
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('location_details', store)

            container.to_layout()
            store_panel.content = BoxLayout(orientation='vertical')
            store_panel.content.add_widget(LocationDetailHeader())
            store_panel.content.add_widget(container.container_display)
            container.generate_data(store.locations.values())

        for panel in sub_panel.tab_list:
            # noinspection PyUnboundLocalVariable
            if panel.text == default_store:
                sub_panel.default_tab = panel
        sub_panel.tab_width = MDApp.get_running_app().root.width / (len(app.db.stores) - 1)
