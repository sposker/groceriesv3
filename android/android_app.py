"""Android version"""

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDRectangleFlatIconButton

from __init__ import *
from android import *
from android.and_card import AndroidItemCard
from android.and_toggle import LongPressToggle
from android.screens import SelectionScreen, PreviewScreen, ListLoaderScreen, SaveScreen
from logical.io_manager import NetworkManager
from logical.state import ListState
from widget_sections.selection import GroupDisplay
from widget_sections.shared_preview import ItemCardContainer

APP_KV_PATH = r'android/android_kv/_android_root.kv'
KV_WIDGETS = ['preview_screen',
              'save_and_load_screens',
              'search_screen',
              'selection_screen',
              'nav_drawer',
              'details_screen',
              'android_dialogs',
              ]

widgets_list = ['android/android_kv/' + s + '.kv' for s in KV_WIDGETS]


class MobileApp(MDApp):

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

    screen_manager = ObjectProperty()

    def __init__(self, **kwargs):
        self.set_theme()
        super().__init__(**kwargs)

        self.db = None
        self.toolbar = None
        self.list_state = None
        self.runner = None
        self.io_manager = None
        self.toggle_cls = None

    def build(self):
        Builder.load_file(APP_KV_PATH)
        for f in widgets_list:
            Builder.load_file(f)
        root_ = Runner()
        self.screen_manager = root_.ids.swiper_manager
        self.toolbar = root_.ids.base_toolbar
        return root_

    def set_theme(self):
        """Colors for app; must be done as part of `__init__` method"""
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.accent_hue = '700'
        self.theme_cls.theme_style = 'Dark'

    def load_data(self):
        """Called on entering load screen"""
        # Load data from IO sources
        self.io_manager = NetworkManager()
        self.db = self.io_manager.create_database()

        # Set up widgets representing the state of the app (Model in MVC)
        ListState.container = ItemCardContainer()
        ListState.view_cls = AndroidItemCard
        self.list_state = ListState()
        self.toggle_cls = LongPressToggle
        GroupDisplay._header_height = self.item_row_height

        # Populate selection widgets and associate them with app state (Controller in MVC)
        load = self.screen_manager.current_screen
        screens = [SelectionScreen(name="picker"),
                   PreviewScreen(name="preview"),
                   ListLoaderScreen(name='file_picker'),
                   SaveScreen(name='save')
                   ]

        for s in screens:
            self.screen_manager.add_widget(s)

        self.toolbar.disabled = False
        self.screen_manager.current = "picker"
        self.screen_manager.remove_widget(load)

        # Automatically load a pool in progress, if available
        self.list_state.request_pool_load()

    def exit_routine(self, gro_list=None, pool=None):
        if gro_list:
            self.db.set_new_defaults(pool)
            self.io_manager.dump_database(self.db)
        MDApp.get_running_app().stop()


class ContentNavigationDrawer(BoxLayout):
    """Shown on root screen"""


class Runner(BoxLayout):
    """App root"""


class NavigationItem(MDRectangleFlatIconButton):
    icon = StringProperty()
    screen_text = StringProperty()

    def on_release(self):
        app = MDApp.get_running_app()
        app.screen_manager.current = self.screen_text
        nd = app.root.ids.nav_drawer
        nd.toggle_nav_drawer()
        nd.__state = 'close'

