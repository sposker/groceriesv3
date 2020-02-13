import datetime
import os

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from logical.database import Database
from logical.pools_and_lists import ItemPool
from logical.state import ListState
from widget_sections.preview import ItemCard, ItemCardContainer
from windows import screenwidth, screenheight
from __init__ import *


APP_KV_PATH = r'windows/win_kv/_win_root.kv'
KV_WIDGETS = ['preview', 'search', 'selection', 'navbar', 'dialogs']

Window.size = (screenwidth / 2, screenheight / 2)
Window.borderless = True
Window.position = 'custom'
Window.left = screenwidth/2 - Window.size[0]/2
Window.top = screenheight/2 - Window.size[1]/2
Window.icon = 'data\\src\\main.ico'
widgets_list = ['windows/win_kv/' + s + '.kv' for s in KV_WIDGETS]


# noinspection PyAttributeOutsideInit
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
    screenheight = screenheight
    screenwidth = screenwidth

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_nonetypes()
        self.set_theme()
        self.path = 'data/username/username.yaml'
        self.db = Database(item_db=self.path)

    def build(self):
        """Load various .kv files and create screen manager."""
        Builder.load_file(APP_KV_PATH)
        for f in widgets_list:
            Builder.load_file(f)
        self.sm = GroManager()
        return self.sm

    def set_theme(self):
        """Colors for app; must be done as part of `__init__` method"""
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.primary_hue = '500'
        self.theme_cls.accent_palette = 'Orange'
        self.theme_cls.accent_hue = '700'
        self.theme_cls.theme_style = 'Dark'

    def load_user_settings(self):
        """Reads the user settings file for things like save path, etc."""
        # 'TODO: specify what this loads'
        try:
            self._real_user_load()
        except FileNotFoundError:
            self._load_defaults()

    def load_data(self):
        self.load_user_settings()
        ListState.container = ItemCardContainer()
        ListState.view_cls = ItemCard
        self.list_state = ListState()

        s = MainScreen(name='main')
        self.sm.add_widget(s)

        now = str(datetime.datetime.now()).split(" ")[0]  # Just the date
        now = now.replace('-', '.')  # Path-friendly formatting used for writing to disk

        for _, _, pools in os.walk(self.pools_path):
            for pool in pools:
                if now in pool:  # today's date matches the date of an item list
                    itempool = ItemPool.from_file(os.path.join(self.pools_path, pool))
                    ListState.instance.populate_from_pool(itempool)

    def _set_nonetypes(self):
        """Create app attributes to be overwritten by user settings or defaults"""

        attrs = {
            'sm',
            'username',
            'credentials_path',
            'pools_path',
            'old_db_path',
            'lists_path',
            'theme_path',
        }

        for attr in attrs:
            setattr(self, attr, None)

    def exit_routine(self, gro_list=None, pool=None):
        if gro_list:
            self.db.set_new_defaults(pool)
            self.db.dump_local()
        MDApp.get_running_app().stop()

    def _real_user_load(self):
        """Load user data"""  # TODO
        raise FileNotFoundError

    def _load_defaults(self):

        cwd = os.getcwd()
        attrs = {
            'username': 'username',
            'credentials_path': os.path.join(cwd, 'data/credentials.txt'),
            'pools_path': os.path.join(cwd, 'data/username/pools'),
            'old_db_path': os.path.join(cwd, 'data/username/old_database'),
            'lists_path': os.path.join(cwd, 'data/username/lists'),
        }

        for k, v in attrs.items():
            setattr(self, k, v)


class GroManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change(self):
        pass


class MainScreen(Screen):
    """Main Screen for app"""


class LoadScreen(Screen):
    """Loading screen with simple animation"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self._trigger = Clock.create_trigger(self.real_load, 2)

    def real_load(self, _):
        """Displays load screen while app builds itself"""
        self.app.load_data()
        return Clock.schedule_once(self.swap_screen)

    def swap_screen(self, _):
        """Once loading is complete, swap the screen"""
        return setattr(self.app.sm, 'current', "main")

    def on_enter(self, *args):
        self._trigger()


if __name__ == '__main__':
    WinApp().run()
