from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton

from widget_sections.selection import GroupScrollBar


class SpinnerButton(MDFlatButton):
    """Button inside dropdown"""

    def jump(self):
        return NavBarSpinner.jump(self.text)


class NavBarSpinner(Spinner):
    """Spinner for groups"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        NavBarSpinner.values = [k.name for k in app.db.items_by_group]

    @staticmethod
    def jump(text, padding=120):

        i = GroupScrollBar.instance

        widgets_list = i.heights[text]
        i.scroll_to(widgets_list[0], padding=padding)
        try:
            NavBarSpinner.jump_anim(widgets_list[1])
        except AttributeError:
            pass


class WinNavBar(BoxLayout):
    """Windows toolbar"""

    @staticmethod
    def minimize():
        Window.minimize()

    @staticmethod
    def toggle_max(btn):
        """Maximize and restore the window"""
        try:
            _ = Window.is_maximized
        except AttributeError:
            Window.is_maximized = False

        if Window.is_maximized:
            Window.restore()
            btn.icon = 'window-maximize'
            Window.is_maximized = False
        else:
            Window.maximize()
            btn.icon = 'window-restore'
            Window.is_maximized = True
