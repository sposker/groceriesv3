"""Iterate through all items and adjust their group"""

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton

from access_app import access_dicts
from access_app.access_dicts import ItemDetail
from logical.items import DisplayGroup
from windows import screenwidth, screenheight
from logical import as_list, as_string

GENERAL = ['preview', 'search', 'selection']
SPECIFIC_WIN = ['win_navbar', 'dialogs']
APP_KV_PATH = r'windows\windows.kv'

DARK_HIGHLIGHT = BACKGROUND_COLOR = (0.07058823529411765, 0.07058823529411765, 0.07058823529411765, 1)  # Dark gray
ELEMENT_COLOR = (0.12549019607843137, 0.12549019607843137, 0.12549019607843137, 1)  # Medium Gray
LIGHT_HIGHLIGHT = (0.39215686274509803, 0.396078431372549, 0.41568627450980394, 1)  # Lighter Gray
TEXT_COLOR = (0.8862745098039215, 0.8862745098039215, 0.8862745098039215, 1)  # Lightest Gray
APP_COLORS = [DARK_HIGHLIGHT, BACKGROUND_COLOR, ELEMENT_COLOR, LIGHT_HIGHLIGHT, TEXT_COLOR]

ITEM_ROW_HEIGHT = 72
TEXT_BASE_SIZE = 40

Window.size = (screenwidth / 1.5, screenheight / 1.25)
# Window.borderless = True
Window.position = 'custom'
Window.left = screenwidth/2 - Window.size[0]/2
Window.top = screenheight/2 - Window.size[1]/2
Window.icon = 'data\\src\\main.ico'
widgets_list = ['widget_sections/win' + s + '.kv' for s in GENERAL] + ['windows/' + s + '.kv' for s in SPECIFIC_WIN]



class MySpinnerButton(MDFlatButton):
    pass


class AccessSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = MDApp.get_running_app().db
        self.values = [grp.name for grp in self.db.groups.values()]


class AccessBaseLayout(BoxLayout):
    """Shared properties across various layout classes"""


class ModGroupLayout(BoxLayout):
    """Allows adjusting display group names and order"""

    group_name = StringProperty()
    group_uid = StringProperty()

    def __init__(self, attrs, **kwargs):
        super().__init__(**kwargs)
        self.group_name = attrs['group_name']
        self.group_uid = attrs['group_uid']


class GroupItemLayout(AccessBaseLayout):
    """Entry for mapping display groups to items"""


class ItemDetailsLayout(RecycleDataViewBehavior, AccessBaseLayout):
    """For editing item details, no mappings."""

    rv = None  # RecycleView instance
    db = None

    item = ObjectProperty()
    item_uid = StringProperty()
    item_name = StringProperty()
    item_group_uid = StringProperty()
    item_group_name = StringProperty()
    item_default_0 = StringProperty()
    item_default_1 = StringProperty()
    item_default_2 = StringProperty()
    item_note = StringProperty()

    def __init__(self):
        super().__init__()
        self._old_data = None
        self._widget_refs = None

    def update_value(self):
        """Save the current row of values"""

        copy = self.data_copy  # Run this for the first time

        self.item.name = self.widget_refs['item_name'].text
        self.item.group = self._convert_group()
        self.item.defaults = self._convert_defaults()
        self.item.note = self.widget_refs['item_note'].text

        index = self.rv.data.index(copy)
        new_value = ItemDetail(self.item).kv_pairs
        self.rv.data[index] = new_value
        del self.data_copy
        self.rv.refresh_from_data()

    def reset_values(self):
        """Simply refresh the data without updating it, restoring previous values."""
        self.rv.refresh_from_data()

    def _convert_defaults(self) -> list:
        """Build a new list of defaults based on input"""
        defaults = self.item.defaults
        while len(defaults) < 3:
            defaults.append(None)
        new_values = [self.widget_refs['defaults' + str(n)].text for n in range(2)]

        new_defaults = []
        for pair, val in zip(self.item.defaults, new_values):
            if val == ' ':
                continue
            if val.upper() == 'N':
                val = ''
            try:
                t, num = pair
            except TypeError:
                import time
                t, num = time.time(), pair
            new_defaults.append((t, val))
        return new_defaults

    def _convert_group(self) -> DisplayGroup:
        """Find a new group object based on input"""
        text = self.widget_refs['group_name'].text
        if text == self.item.group.name:
            return self.item.group
        else:
            if not self.db:
                ItemDetailsLayout.db = MDApp.get_running_app().db
            for group in self.db.groups.values():
                if group.name == text:
                    return group

    @property
    def data_copy(self):
        if self._old_data is None:
            self._old_data = ItemDetail(self.item).kv_pairs
        return self._old_data

    @data_copy.deleter
    def data_copy(self):
        self._old_data = None

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


class ItemLocationLayout(AccessBaseLayout):
    """Entry for mapping location to item"""


class ModLocationsLayout(AccessBaseLayout, RecycleDataViewBehavior, ):
    """Allows adjusting Location names and order"""


class RecycleViewContainer(RecycleBoxLayout):
    """Container holding sub-layouts."""


class AccessTabbedPanel(TabbedPanel):
    """Tabbed panels root"""

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        for name, section in self.ids.items():
            try:
                self.populate(name, section)
            except KeyError:
                print(f'Passed {name=}')
            # else:
            #     print(f'Added {name=}')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def populate(self, name, section):
        child_cls, list_dict = MDApp.get_running_app().mapping[name]
        if not name == 'mod_groups':
            rv = AccessRecycleView(list_dict, viewclass=child_cls)
            child_cls.rv = rv
        else:
            rv = BoxLayout(orientation='vertical',
                           spacing=8)
            for nested in list_dict:
                widget = child_cls(nested)
                rv.add_widget(widget)
        section.content.add_widget(rv)

        # Clock.schedule_once(lambda _: rv.refresh_from_data())
        # Clock.schedule_once(lambda _: rv.refresh_views())


class AccessMidButton(MDRectangleFlatIconButton):
    """Button that is visible on all tabbed panel screens"""

    def add_new_entry(self, tab):
        ...

    def update_from_view(self, tab):
        ...

    def dump_data(self, tab):
        ...

    @staticmethod
    def stop_app():
        return MDApp.get_running_app().stop()


class AccessRoot(BoxLayout):
    """Root for the access app"""


class AccessRecycleView(RecycleView):
    """Holds various layouts in different sections of app."""

    def __init__(self, data_dict, viewclass=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data_dict
        self.viewclass = viewclass


class AccessApp(MDApp):
    mapping = {
        'mod_groups': (ModGroupLayout, access_dicts.group_details),
        'item_details': (ItemDetailsLayout, access_dicts.item_details),
        # 'locs_map': (Button, access_dicts.loc_maps),
        # 'mod_locs': (ModLocationsLayout, access_dicts.loc_details),
    }

    dh_color = DARK_HIGHLIGHT
    bg_color = BACKGROUND_COLOR

    elem_color = ELEMENT_COLOR
    elem_color_string = as_string(elem_color)
    elem_color_list = as_list(elem_color)

    lh_color = LIGHT_HIGHLIGHT
    text_color = TEXT_COLOR

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]

    hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
    # text_base_size = TEXT_BASE_SIZE
    # item_row_height = ITEM_ROW_HEIGHT
    screenheight = screenheight
    screenwidth = screenwidth

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('app_init')
        self.set_theme()
        self.db = access_dicts.db

    def set_theme(self):
        """Must be done as part of `__init__` method"""
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.accent_hue = '700'
        self.theme_cls.theme_style = 'Dark'

    def build(self):
        Builder.load_file(APP_KV_PATH)
        Builder.load_file('access_app/access_elements.kv')
        Builder.load_file('access_app/access_layouts.kv')
        return AccessRoot()















