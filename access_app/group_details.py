"""Contains classes used for modifying `DisplayGroup` order and names"""

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

from access_app.bases import DataGenerator, LayoutContainer


class GroupDetailLogic:
    """"""

    def shift_up(self):
        ...


# noinspection PyRedeclaration
class GroupDetailRow(DataGenerator, GroupDetailLogic):
    """A row representing a single `DisplayGroup`.
    Inherits `BoxLayout` properties from `DataGenerator`.
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
        for row in view_layouts:
            self.container_display.add_widget(row)

    def to_layout(self):
        self.container_display = BoxLayout(
            orientation='vertical',
            spacing=8,
        )


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
