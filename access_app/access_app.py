from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from __init__ import *
from access_app import TEXT_BASE_SIZE, ITEM_ROW_HEIGHT, screenheight, popup_scale, screenwidth, widgets_list, \
    APP_KV_PATH
from access_app.bases import ContainerFactory, DataFactory
from access_app.group_details import GroupDetailContainer, GroupDetailRow
from access_app.item_details import ItemDetailContainer, ItemDetailData
from access_app.item_location_mapping import StoreItemMapContainer, LocationMapData
from access_app.location_details import StoreLocationDetailContainer, LocationDetailRow
from logical.io_manager import LocalManager


class AccessRoot(BoxLayout):
    """Main screen content 'root' widget for the access app (real root is the screen manager)"""


class AccessApp(MDApp):
    card_color = CARD_COLOR
    card_color_string = as_string(card_color)
    card_color_list = as_list(card_color)

    bg_color = BACKGROUND_COLOR
    bg_color_string = as_string(bg_color)
    bg_color_list = as_list(bg_color)

    elem_color = ELEMENT_COLOR
    elem_color_string = as_string(elem_color)
    elem_color_list = as_list(elem_color)

    text_color = TEXT_COLOR
    text_color_string = as_string(text_color)
    text_color_list = as_list(text_color)

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]

    hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
    text_base_size = TEXT_BASE_SIZE
    item_row_height = ITEM_ROW_HEIGHT
    popup_height = screenheight * popup_scale
    popup_width = screenwidth * popup_scale

    container_mapping = {
        'group_details': (GroupDetailContainer, GroupDetailRow),
        'item_details': (ItemDetailContainer, ItemDetailData),
        'map_locations': (StoreItemMapContainer, LocationMapData),
        'location_details': (StoreLocationDetailContainer, LocationDetailRow),
    }
    data_mapping = {k: v[1] for k, v in container_mapping.items()}
    container_factory = ContainerFactory(**container_mapping)
    data_factory = DataFactory(**data_mapping)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_theme()

        self.db = None
        self.list_state = None
        self.screen_manager = None
        self.io_manager = None
        self.toggle_cls = None

    def set_theme(self):
        """Must be done as part of `__init__` method"""
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.accent_hue = '700'
        self.theme_cls.theme_style = 'Dark'

    def build(self):
        for file in widgets_list:
            Builder.load_file(file)
        Builder.load_file(APP_KV_PATH)
        self.screen_manager = AccessManager()
        return self.screen_manager

    def load_data(self):
        self.io_manager = LocalManager()
        self.db = self.io_manager.create_database()

        s = AccessMainScreen(name='Amain')
        self.screen_manager.add_widget(s)


class AccessManager(ScreenManager):
    """Manager for access app"""


class AccessMainScreen(Screen):
    """Main Screen for access app; contains AccessRoot defined in kvlang.
     The root holds a tabbed panel view with various tabs representing different data sets."""


class AccessLoadScreen(Screen):
    """Access loading screen"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self._trigger = Clock.create_trigger(self.real_load, 1)

    def real_load(self, *_):
        """Displays load screen while app builds itself"""
        self.app.load_data()
        return Clock.schedule_once(self.swap_screen)

    def swap_screen(self, *_):
        """Once loading is complete, swap the screen"""
        return setattr(self.app.screen_manager, 'current', "Amain")

    def on_enter(self, *args):
        self._trigger()













