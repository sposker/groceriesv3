"""Iterate through all items and adjust their group"""

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDRectangleFlatIconButton, MDRectangleFlatButton, MDFlatButton

from access_app.access_containers import ItemDetailContainer, GroupDetailContainer, StoreItemMapContainer, \
    StoreLocationDetailContainer, ContainerFacotry
from access_app.access_view_registers import GroupDetail, ItemDetail, LocationMap, LocationDetail
from logical.groups_and_items import DisplayGroup
from logical.io_manager import LocalManager
from __init__ import *
from access_app import *


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

    factory_mapping = {
        'mod_groups': GroupDetailContainer,
        'item_details': ItemDetailContainer,
        'locs_map': StoreItemMapContainer,
        'mod_locs': StoreLocationDetailContainer,
    }
    factory = ContainerFacotry(**factory_mapping)

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
        return setattr(self.app.screen_manager, 'current', "Amain")

    def on_enter(self, *args):
        self._trigger()













