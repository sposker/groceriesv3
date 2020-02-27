"""Contains classes used for modifying `DisplayGroup` order and names"""

from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer
from logical.groups_and_items import DisplayGroup


class GroupDetailLogic:
    """Methods bound to widgets that interact with the `GroupDetailRow`"""

    element = None

    def create_new(self):
        """Add a new DisplayGroup to display via factory"""
        g = DisplayGroup('NewGroup')
        MDApp.get_running_app().db.groups[g.uid] = g
        self.refresh_from_data()

    def shift(self, direction):
        """Attempt to change a `DisplayGroup`s uid."""

        uid = self.element.uid
        z_factor = len(uid) - 1
        index = int(uid[1:])
        app = MDApp.get_running_app()
        try:
            other_group = app.db.groups['g' + str(index + direction).zfill(z_factor)]
        except KeyError:
            return  # Invalid selection, usually first or last item
        else:
            other_group.uid = self.element.uid
            self.element.uid = 'g' + str(index + direction).zfill(z_factor)
            app.db.groups.update({self.element.uid: self.element, other_group.uid: other_group})
            return True  # Successfully swapped group uids (and therefore sort order)

    def swap(self, value):
        """Initiate swapping values between two groups."""
        result = self.shift(value)
        if result:
            self.refresh_from_data()

    def refresh_from_data(self):
        tab = self.parent.parent.parent
        tab.remove_widget(tab.children[0])
        tab.populate()


class GroupDetailRow(DataGenerator, GroupDetailLogic):
    """A row representing a single `DisplayGroup`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Inherits methods for manipulating widgets from `GroupDetailLogic`.
    Factory must yield actual objects to populate a `BoxLayout`.
    """

    @property
    def kv_pairs(self):
        kv_pairs = {
            'group_name': self.element.name,
            'group_uid': self.element.uid,
        }
        return kv_pairs

    @property
    def group_name(self):
        return self.element.name

    @property
    def group_uid(self):
        return self.element.uid


class GroupDetailContainer(LayoutContainer):
    """The container which holds GroupDetailRows"""

    def generate_data(self, elements):
        app = MDApp.get_running_app()
        view_layouts = sorted(app.data_factory.get('group_details', elements), key=lambda x: x.sort_key)
        self.fill_container(view_layouts, 14)

    def to_layout(self):
        self.container_display = BoxLayout()


class ModGroupContent(BoxLayout):
    """Builds the content of this tabbed panel (0).
    Primary content is a `BoxLayout` instance.
    """

    def populate(self):
        app = MDApp.get_running_app()
        container = app.container_factory.get('group_details')
        container.to_layout()
        container.generate_data(app.db.groups.values())
        self.add_widget(container.container_display)
