"""Iterate through all items and adjust their group"""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton, MDRectangleFlatButton

from access_app.access_dicts import GroupDetail, ItemDetail, LocationMap, LocationDetail
from access_app.tabbed_panel_builders import populate_mod_group, populate_item_details, populate_location_mapping, \
    populate_location_details
from logical import as_list, as_string
from logical.database import Database
from logical.groups_and_items import DisplayGroup
from windows import screenwidth, screenheight

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

# db = Database(item_db='data/username/username.yaml')


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


class ViewSortButton(MDRectangleFlatButton):
    """Buttons for sorting"""

    def sort(self):
        # print(self.rv_base.content.children[0])
        rv = self.rv_base.content.children[0]
        data = sorted(rv.data, key=lambda x: x[self.sort_key])
        if self.sort_dir == 'ascending':
            self.sort_dir = 'descending'
        else:
            self.sort_dir = 'ascending'
            data.reverse()
        rv.data = data
        rv.refresh_from_data()


class ItemDetailsLayout(AccessBaseLayout):
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

        for index, nested in enumerate(self.rv.data):
            if nested['item_uid'] == self.item_uid:
                break

        new_value = ItemDetail(self.item).kv_pairs
        self.rv.data[index] = new_value
        self.rv.refresh_from_data()

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

    @classmethod
    def update_all(cls):
        new_data = []



class ItemLocationLayout(AccessBaseLayout):
    """Entry for mapping location to item"""



class StoreSubTabbed(TabbedPanel):
    """Entry for mapping location to item"""

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)





class ModLocationsLayout(AccessBaseLayout,):
    """Allows adjusting Location names and order"""

    location_name = StringProperty()
    location_uid = StringProperty()

    def __init__(self, attrs, **kwargs):
        super().__init__(**kwargs)
        self.group_name = attrs['location_name']
        self.group_uid = attrs['location_uid']


class RecycleViewContainer(RecycleBoxLayout):
    """Container holding sub-layouts."""


class AccessRecycleView(RecycleView):
    """Holds various layouts in different sections of app."""

    def __init__(self, data_dict, viewclass=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data_dict
        self.viewclass = viewclass


class AccessTabbedPanel(TabbedPanel):
    """Tabbed panels root"""

    mapping = {
        'mod_groups': (populate_mod_group, GroupDetail, ModGroupLayout,),
        'item_details': (populate_item_details, ItemDetail, AccessRecycleView, ItemDetailsLayout, ),
        'locs_map': (populate_location_mapping, LocationMap, TabbedPanel, ItemLocationLayout),
        'mod_locs': (populate_location_details, LocationDetail, TabbedPanel, ModLocationsLayout),
    }

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        for name, section in self.ids.items():
            try:
                args = self.mapping[name]
            except KeyError:
                print(f'Passed {name=}')
            else:
                self.populate(section, *args)


    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     for name, section in self.ids.items():
    #         try:
    #             args = self.mapping[name]
    #         except KeyError:
    #             print(f'Passed {name=}')
    #         else:
    #             self.populate(section, *args)

    def populate(self, section, callback, *args):
        db = MDApp.get_running_app().db
        content = callback(db, *args)
        section.content.rv_ref = content
        section.content.add_widget(content)

        # Clock.schedule_once(lambda _: rv.refresh_from_data())
        # Clock.schedule_once(lambda _: rv.refresh_views())


class AccessMidButton(MDRectangleFlatIconButton):
    """Button that is visible on all tabbed panel screens"""

    mapping = {
        'Group Names & Order': None,
        'Item Details': None,
        'Item: Location Mapping': None,
        'Location Names & Order': None
    }

    def add_new_entry(self, tab):
        return self.mapping[tab.text]

    def update_from_view(self, tab):
        ...

    def dump_data(self, tab):
        ...

    @staticmethod
    def stop_app():
        return MDApp.get_running_app().stop()


class AccessRoot(BoxLayout):
    """Root for the access app"""



class AccessManager(ScreenManager):
    """Manager for access app"""


class AccessMainScreen(Screen):
    """Main Screen for access app"""


class AccessLoadScreen(Screen):
    """Access loading screen"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self._trigger = Clock.create_trigger(self.real_load, 1)

    def real_load(self, _):
        """Displays load screen while app builds itself"""
        self.app.load_data()
        return Clock.schedule_once(self.swap_screen)

    def swap_screen(self, _):
        """Once loading is complete, swap the screen"""
        return setattr(self.app.sm, 'current', "Amain")

    def on_enter(self, *args):
        self._trigger()


class AccessApp(MDApp):

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
    text_base_size = TEXT_BASE_SIZE
    # item_row_height = ITEM_ROW_HEIGHT
    screenheight = screenheight
    screenwidth = screenwidth

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_theme()
        self.db = Database('data/username/username.yaml')
        self.sm = None

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
        self.sm = AccessManager()
        return self.sm

    def load_data(self):
        s = AccessMainScreen(name='Amain')
        self.sm.add_widget(s)













