import datetime
import os

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from logical.pools_and_lists import ItemPool
from logical.state import ListState
from widget_sections.preview import ItemCard, ItemCardContainer
from windows import screenwidth, screenheight
from logical import as_list, as_string
from logical.database import Database


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

Window.size = (screenwidth / 2, screenheight / 2)
Window.borderless = True
Window.position = 'custom'
Window.left = screenwidth/2 - Window.size[0]/2
Window.top = screenheight/2 - Window.size[1]/2
Window.icon = 'data\\src\\main.ico'
widgets_list = ['widget_sections/win' + s + '.kv' for s in GENERAL] + ['windows/' + s + '.kv' for s in SPECIFIC_WIN]


# noinspection PyAttributeOutsideInit
class WinApp(MDApp):

    dh_color = DARK_HIGHLIGHT
    dh_color_string = as_string(dh_color)
    dh_color_list = as_list(dh_color)

    bg_color = BACKGROUND_COLOR
    bg_color_string = as_string(bg_color)
    bg_color_list = as_list(bg_color)

    elem_color = ELEMENT_COLOR
    elem_color_string = as_string(elem_color)
    elem_color_list = as_list(elem_color)

    lh_color = LIGHT_HIGHLIGHT
    # lh_color_string = as_string(lh_color)
    # lh_color_list = as_list(lh_color)

    text_color = TEXT_COLOR
    text_color_string = as_string(text_color)
    text_color_list = as_list(text_color)

    # End Config properties
    # Begin Misc

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]

    hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
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

    def exit_routine(self, gro_list=None):
        if gro_list:
            self.db.set_new_defaults(gro_list)
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
