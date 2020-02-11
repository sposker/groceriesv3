from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton

from kivymd.uix.textfield import MDTextFieldRound
from kivymd.uix.tooltip import MDTooltip

from logical.state import ListState


class MyMDIconButton(MDIconButton, MDTooltip):
    """Larger icons and tooltip behavior"""

    group = StringProperty()
    members = set()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.members.add(self)

    def animation_tooltip_show(self, interval):
        if not self._tooltip:
            return
        (
            Animation(_scale_x=1, _scale_y=1, d=0.4)
            + Animation(opacity=1, d=0.4)
        ).start(self._tooltip)

    def on_release(self):
        """Change color for active sort type"""
        if self.group:
            app = MDApp.get_running_app()
            self.text_color = app.theme_cls.accent_color
            for btn in self.members:
                if btn.group == self.group and btn != self:
                    btn.text_color = app.theme_cls.primary_color


class ListFunctionsBar(BoxLayout):
    """Layout holding useful functions for list and search"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._assign_callbacks)

    def _assign_callbacks(self, _):
        for c in self.children:
            c.bind(on_release=lambda x: getattr(self, x.name)(x))

    @staticmethod
    def alphabetical(_):
        """Set sort order to A-Z"""
        ListState.instance.sort_type = 'name'
        ListState.instance.sort_cards()
        # print('outside state context')

    @staticmethod
    def group(_):
        """Set sort order to item group"""
        ListState.instance.sort_type = 'group'
        ListState.instance.sort_cards()

    @staticmethod
    def time(_):
        """Set sort order to time added"""
        ListState.instance.sort_type = 'time'
        ListState.instance.sort_cards()

    @staticmethod
    def toggle_asc_desc(btn):
        """Change sort order to ascending or descending"""
        btn.icon = ({'sort-ascending', 'sort-descending'} - {btn.icon}).pop()
        btn.tooltip_text = ({"Current: Ascending", "Current: Descending"} - {btn.tooltip_text}).pop()
        ListState.sort_desc = not ListState.sort_desc
        ListState.instance.sort_cards()

    @staticmethod
    def open(_):
        Factory.FilePickerDialog().open()

    @staticmethod
    def reset(_):
        """Clear the list"""
        Factory.ClearListDialog().open()

    @staticmethod
    def save(_):
        """Launch the save dialog"""
        gro_list = ListState.instance.convert_to_pool()
        Factory.SaveDialog(gro_list).open()


class SearchBar(MDTextFieldRound):
    """Search for and add items from keyboard"""
