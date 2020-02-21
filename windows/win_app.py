from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from __init__ import *  # general app settings
from logical.io_manager import LocalManager
from logical.state import ListState
from widget_sections.selection import PairedToggleButtons, GroupDisplay
from widget_sections.shared_preview import ItemCardContainer
from windows import *  # windows specific settings
from windows.win_card import WinItemCard


class WinApp(MDApp):

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

    # hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
    text_base_size = TEXT_BASE_SIZE
    item_row_height = ITEM_ROW_HEIGHT
    popup_height = screenheight * popup_scale
    popup_width = screenwidth * popup_scale

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_theme()

        self.db = None
        self.list_state = None
        self.screen_manager = None
        self.io_manager = None
        self.toggle_cls = None

    def build(self):
        """Load various .kv files and create screen manager."""
        Builder.load_file(APP_KV_PATH)
        for f in widgets_list:
            Builder.load_file(f)
        self.screen_manager = GroManager()
        return self.screen_manager

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
        self.io_manager = LocalManager()
        self.db = self.io_manager.create_database()

        # Set up widgets representing the state of the app (Model in MVC)
        ListState.container = ItemCardContainer()
        ListState.view_cls = WinItemCard
        self.toggle_cls = PairedToggleButtons
        self.list_state = ListState()
        GroupDisplay._header_height = self.item_row_height * 11/8

        # Populate selection widgets and associate them with app state (Controller in MVC)
        load = self.screen_manager.current_screen
        s = MainScreen(name='main')
        self.screen_manager.add_widget(s)
        self.screen_manager.remove_widget(load)

        # Automatically load a pool in progress, if available (adjusts View in MVC)
        self.io_manager.load_pool()

    def exit_routine(self, pool=None):
        if self.io_manager.should_update:
            self.db.set_new_defaults(pool)
            self.io_manager.dump_database()
        MDApp.get_running_app().stop()


class GroManager(ScreenManager):
    """Screen Manager-- used more heavily in other OS versions of app."""


class MainScreen(Screen):
    """Main Screen for app"""


class LoadScreen(Screen):
    """Loading screen with simple animation"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self._trigger = Clock.create_trigger(self.real_load, 2)

    def on_enter(self, *args):
        self._trigger()

    def real_load(self, _):
        """Now that loading splash is displayed, begin actually loading the app"""
        self.app.load_data()
        return Clock.schedule_once(self.swap_screen)

    def swap_screen(self, _):
        """Once loading is complete, swap the screen"""
        return setattr(self.app.screen_manager, 'current', "main")


if __name__ == '__main__':
    WinApp().run()
