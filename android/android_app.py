"""Android version"""
import datetime
import requests

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.card import MDCard

from logical.state import ListState
from widget_sections.preview import ItemCardContainer, ItemCard
from logical.database import Database
from android.screens import SelectionScreen, PreviewScreen, DetailsScreen
# from android import *
from __init__ import *

APP_KV_PATH = r'android/android_kv/_android_root.kv'
KV_WIDGETS = ['preview_screen',
              'search_screen',
              'selection_screen',
              'nav_drawer',
              'details_screen',
              'android_dialogs',
              ]

widgets_list = ['android/android_kv/' + s + '.kv' for s in KV_WIDGETS]


class MobileApp(MDApp):
    db = None
    db_path = None
    list_state = None
    runner = None
    host = '192.168.1.241'
    read_port = 42209
    send_list_port = 42210
    db_port = 42211

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

    # End Config properties
    # Begin Misc

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]
    text_base_size = TEXT_BASE_SIZE
    item_row_height = ITEM_ROW_HEIGHT

    swiper_manager = ObjectProperty()

    def __init__(self, **kwargs):
        self.set_theme()
        super().__init__(**kwargs)
        self.sm = None
        self.shopping_list = None

    def set_theme(self):
        """Colors for app; must be done as part of `__init__` method"""
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.accent_hue = '700'
        self.theme_cls.theme_style = 'Dark'

    def build(self):
        Builder.load_file(APP_KV_PATH)
        for f in widgets_list:
            Builder.load_file(f)
        start_screen = Runner()
        self.swiper_manager = start_screen.ids.swiper_manager
        return start_screen

    def load_data(self):

        self.db = Database('data/username/username.yaml')  # TODO

        ListState.container = ItemCardContainer()
        ListState.view_cls = ItemCard
        self.list_state = ListState()

        load = self.swiper_manager.current_screen
        screens = [SelectionScreen(name="picker"), PreviewScreen(name="preview"), DetailsScreen(name="details")]
        for s in screens:
            self.swiper_manager.add_widget(s)

        self.swiper_manager.current = "picker"
        self.swiper_manager.remove_widget(load)

        # lists = f'http://{self.host}:{self.read_port}/lists'
        # r = requests.get(lists)
        # items = ''
        # now = str(datetime.datetime.now()).split(" ")[0]
        # now = now.replace('-', '.')

        # for file in r:
        #     items += str(file.decode())
        #
        # lines = items.split('\n')
        #
        # for line in lines:
        #     if now in line:
        #         lists += '/' + now + '.ListWriter.txt'
        #         file = requests.get(lists)
        #         self.load_list(file.content, from_bytes=True)


class Runner(BoxLayout):
    """Handles swipe events"""


class MyCard(MDCard):
    text = StringProperty("")



