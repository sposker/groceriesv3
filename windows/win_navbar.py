from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDToolbar

from widget_sections.selection import GroupScrollBar, DisplaySubsection


class SpinnerButton(MDFlatButton):
    """Button inside dropdown"""

    def jump(self):
        return NavBarSpinner.jump(self.text)


class NavBarSpinner(Spinner):
    """Spinner for groups"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        NavBarSpinner.values = [k.name for k in app.db.groups.values()]
        Clock.schedule_once(self.do_app_iter, 1)

    def do_app_iter(self, _):
        app = MDApp.get_running_app()
        for k, v in app.sm.current_screen.ids.items():
            print(k, v)

    @staticmethod
    def jump(text, padding=120):

        i = GroupScrollBar.instance

        widgets_list = i.heights[text]
        i.scroll_to(widgets_list[0], padding=padding)
        try:
            NavBarSpinner.jump_anim(widgets_list[1])
        except AttributeError:
            pass

    # @property
    # def width(self):
    #     return super().width
    #
    # @property
    # def _width(self):
    #     if x := DisplaySubsection.last_child:
    #         return x.width
    #     else:
    #         return 246


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

    # @staticmethod
    # def exit_dialogue(*_):
    #     Factory.ExitDialog().open()

# class SpinnerDropdown(DropDown)