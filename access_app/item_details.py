from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

from access_app.access_misc_widgets import AccessRecycleView
from access_app.bases import DataGenerator, LayoutContainer
from logical.groups_and_items import DisplayGroup, GroceryItem


class ItemDetailLogic(BoxLayout):
    """Methods bound to widgets that interact with the `ItemDetailRow`"""

    rv_ref = None

    def __init__(self, **kwargs):
        self._widget_refs = None
        super().__init__(**kwargs)

    def create_new(self):
        """Add a new item to the database via factory"""
        itm = GroceryItem(name='New Item', group='g00')
        MDApp.get_running_app().db.items[itm.uid] = itm
        new_value = next(MDApp.get_running_app().data_factory.get('item_details', (itm,)))
        self.rv_ref.data.append(new_value)
        self.rv_ref.refresh_from_data()

    def _gather_info(self):
        """Update item properties based on entered values"""
        self.item.name = self.widget_refs['item_name'].text
        self.item.group = self._convert_group()
        self.item.defaults = self._convert_defaults()
        self.item.note = self.widget_refs['item_note'].text

    def update_value(self, gather=True):
        """Save the current row of values"""

        if gather:
            self._gather_info()

        for index, nested in enumerate(self.rv_ref.data):
            if nested['item_uid'] == self.item_uid:
                break

        # Use factory to generate an updated set of data for this one item
        new_value = next(MDApp.get_running_app().data_factory.get('item_details', (self.item,)))

        # noinspection PyUnboundLocalVariable
        self.rv_ref.data[index] = new_value
        self.rv_ref.refresh_from_data()

    def reset_values(self):
        """Simply refresh the data without updating it, restoring previous values."""
        return self.update_value(gather=False)

    def _convert_defaults(self) -> list:
        """Build a new list of defaults based on input"""
        defaults = self.item.defaults
        while len(defaults) < 3:
            defaults.append(None)
        new_values = [self.widget_refs['defaults' + str(n)].text for n in range(2)]

        new_defaults = []
        for pair, val in zip(self.item.defaults, new_values):
            if val == '':
                continue
            try:
                t, num = pair
            except TypeError:
                import time
                t, num = int(round(time.time())), pair
            new_defaults.append((t, val))
        return new_defaults

    def _convert_group(self) -> DisplayGroup:
        """Find a new group object based on input"""
        text = self.widget_refs['group_name'].text
        if text == self.item.group.name:
            return self.item.group
        else:
            for group in MDApp.get_running_app().db.groups.values():
                if group.name == text:
                    return group

    @property
    def widget_refs(self) -> dict:
        """Create dict when needed rather than by default"""
        if self._widget_refs is None:
            self._widget_refs = {}
            for w in self.children:
                try:
                    n = getattr(w, 'widget_name')
                except AttributeError:
                    pass
                else:
                    self._widget_refs[n] = w
        return self._widget_refs

    @classmethod
    def update_all(cls):
        ...


class ItemDetailData(DataGenerator):
    """This class translates a `GroceryItem` into a dict representation.
    Factory must yield data rather than actual objects to be compatible with a `RecycleView`.
    """

    @property
    def kv_pairs(self):
        defaults_list = sorted(self.element.defaults.copy(), key=lambda i: i[0])
        defaults_list = [str(num) for _, num in defaults_list]
        while len(defaults_list) < 3:
            defaults_list.append('')
        kv_pairs = {
            'item': self.element,
            'item_uid': self.element.uid,
            'item_name': self.element.name,
            'item_group_uid': self.element.group.uid,
            'item_group_name': self.element.group.name,
            'item_default_0': defaults_list[0],
            'item_default_1': defaults_list[1],
            'item_default_2': defaults_list[2],
            'item_note': self.element.note,
        }
        return kv_pairs


class ItemDetailRow(ItemDetailLogic):
    """View class for `RecycleView`.
    Inherits `BoxLayout` properties and methods from `ItemDetailLogic`.
    """

    item = ObjectProperty()
    item_uid = StringProperty()
    item_name = StringProperty()
    item_group_uid = StringProperty()
    item_group_name = StringProperty()
    item_default_0 = StringProperty()
    item_default_1 = StringProperty()
    item_default_2 = StringProperty()
    item_note = StringProperty()


class ItemDetailContainer(LayoutContainer):
    """The container which holds instances of `ItemDetailRow`"""

    def generate_data(self, elements):
        view_layouts = MDApp.get_running_app().data_factory.get('item_details', elements)
        self.data = sorted(view_layouts, key=lambda x: x.get('item_uid'))

    def to_layout(self):
        self.container_display = AccessRecycleView(self.data, viewclass=ItemDetailRow)
        ItemDetailLogic.rv_ref = self.container_display


class ItemDetailsContent(BoxLayout):
    """Builds the content of this tabbed panel (1).
    Primary content is an `AccessRecycleView` instance.
    """

    def populate(self):
        app = MDApp.get_running_app()
        container = app.container_factory.get('item_details')
        container.generate_data(app.db.items.values())
        container.to_layout()
        self.add_widget(container.container_display)

