from kivy.core.window import Window
from kivy.factory import Factory
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDToolbar


class NavBarSpinner(MDFlatButton):
    """Spinner for groups"""


class WinNavBar(MDToolbar):
    """Windows toolbar"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        WinNavBar.right_action_items = [
            ["window-minimize", self.minimize],
            ["window-maximize", self.toggle_max],
            ["window-close", self.exit_dialogue],
        ]

    @staticmethod
    def minimize(_):
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

    @staticmethod
    def exit_dialogue(*_):
        Factory.ExitDialog().open()
