"""Contains classes used for modifying `DisplayGroup` order and names"""

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer, AccessBaseRow
from logical.groups_and_items import DisplayGroup


class GroupDetailLogic:
    """"""

    def create_new(self):
        """Add a new DisplayGroup via factory"""
        g = DisplayGroup('NewGroup')
        return next(MDApp.get_running_app().data_factory.get('group_details', (g,)))

    def shift(self, direction):
        uid = self.element.uid
        index = int(uid[1:])
        try:
            other_group = MDApp.get_running_app().db.groups['g' + str(index+direction).zfill(2)]
        except KeyError:
            return  # Invalid selection, usually first or last item
        else:
            other_group.uid = self.element.uid
            self.element.uid = 'g' + str(index+direction).zfill(2)
            MDApp.get_running_app().db.groups.update({self.element.uid: self.element, other_group.uid: other_group})
            return True  # Successfully swapped group uids (and therefore sort order)

    def refresh_from_data(self):
        tab = self.parent.parent.parent
        tab.clear_widgets()
        tab.populate()

    def swap(self, value):
        result = self.shift(value)
        if result:
            self.refresh_from_data()


# noinspection PyRedeclaration
class GroupDetailRow(DataGenerator, GroupDetailLogic):
    """A row representing a single `DisplayGroup`.
    Inherits `BoxLayout` properties from `DataGenerator`.
    Inherits methods for manipulating widgets from `GroupDetailLogic`.
    Factory must yield actual objects to populate a `BoxLayout`.
    """

    group_name = StringProperty()
    group_uid = StringProperty()

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
        self.fill_container(view_layouts, 16)

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
        # print(self.children, len(self.children[0].children))
