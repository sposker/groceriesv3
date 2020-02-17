from android.android_app import MobileApp
from android import *

MobileApp.host = '127.0.0.1'
Window.size = (540, 960)
Window.borderless = False
Window.position = 'custom'
MobileApp.item_row_height = ITEM_ROW_HEIGHT / 2
# TEXT_BASE_SIZE = TEXT_BASE_SIZE / 2

if __name__ == '__main__':
    MobileApp().run()
