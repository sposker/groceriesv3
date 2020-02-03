from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.theming import ThemeManager

from windows import screenwidth, screenheight
from logical import as_list, as_string
from logical.database import Database


GENERAL = ['preview', 'search', 'selection']
SPECIFIC_WIN = ['win_navbar', 'dialogues']
APP_KV_PATH = r'windows\windows.kv'

DARK_HIGHLIGHT = (0.1568627450980392, 0.16862745098039217, 0.18823529411764706, 1)  # Darkest Gray
BACKGROUND_COLOR = (0.18823529411764706, 0.19215686274509805, 0.21176470588235294, 1)  # Dark gray
ELEMENT_COLOR = (0.21176470588235294, 0.2235294117647059, 0.25882352941176473, 1)  # Medium Gray
LIGHT_HIGHLIGHT = (0.39215686274509803, 0.396078431372549, 0.41568627450980394, 1)  # Lighter Gray
TEXT_COLOR = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, 1)  # Lightest Gray
APP_COLORS = [DARK_HIGHLIGHT, BACKGROUND_COLOR, ELEMENT_COLOR, LIGHT_HIGHLIGHT, TEXT_COLOR]

ITEM_ROW_HEIGHT = 72
TEXT_BASE_SIZE = 40

Window.size = (screenwidth / 2, screenheight / 2)
Window.borderless = True
Window.position = 'custom'
Window.left = screenwidth/4
Window.top = screenheight/4
Window.icon = 'src\\main.ico'
widgets_list = ['widget_sections/' + s + '.kv' for s in GENERAL] + ['windows/' + s + '.kv' for s in SPECIFIC_WIN]


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
    lh_color_string = as_string(lh_color)
    lh_color_list = as_list(lh_color)

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
        self.sm = None
        self.set_theme()
        self.db = Database('data/username.yaml')

    def build(self):
        Builder.load_file(APP_KV_PATH)
        for f in widgets_list:
            Builder.load_file(f)
        self.sm = GroManager()
        return self.sm

    def set_theme(self):
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '300'
        self.theme_cls.accent_palette = 'Gray'
        self.theme_cls.accent_hue = '800'
        self.theme_cls.theme_style = 'Dark'
        # self.accent_color = [255 / 255, 64 / 255, 129 / 255, 1]


class GroManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('loaded')

    def change(self):
        pass
        Clock.schedule_once(setattr(self, 'current', "main"), 2)


class LoadScreen(Screen):

    @staticmethod
    def do_load(*_):
        app = MDApp.get_running_app()
        return setattr(app.sm, 'current', "main")

    def on_enter(self, *args):
        pass
        # Clock.schedule_once(self.do_load, 2)


if __name__ == '__main__':
    WinApp().run()
