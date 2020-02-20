import ctypes

from kivy.core.window import Window

user32 = ctypes.windll.user32
screenwidth, screenheight = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
# screenwidth, screenheight = 1920, 1080

ITEM_ROW_HEIGHT = 72
TEXT_BASE_SIZE = 40

APP_KV_PATH = r'windows/win_kv/_win_root.kv'
KV_WIDGETS = ['preview', 'search', 'selection', 'navbar', 'dialogs']

Window.size = (2560 / 2, 1440 / 2)
popup_scale = 2560/screenwidth
# print(popup_scale)
Window.borderless = True
Window.position = 'custom'
Window.left = screenwidth/2 - Window.size[0]/2
Window.top = screenheight/2 - Window.size[1]/2
Window.icon = 'data\\src\\main.ico'
widgets_list = ['windows/win_kv/' + s + '.kv' for s in KV_WIDGETS]
