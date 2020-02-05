from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton

from kivymd.uix.textfield import MDTextFieldRound
from kivymd.uix.tooltip import MDTooltip

from widget_sections.preview import ItemCardContainer


class MyMDIconButton(MDIconButton, MDTooltip):
    """Larger icons and tooltip behavior"""

    def animation_tooltip_show(self, interval):
        if not self._tooltip:
            return
        (
            Animation(_scale_x=1, _scale_y=1, d=0.4)
            + Animation(opacity=1, d=0.4)
        ).start(self._tooltip)


class ListFunctionsBar(BoxLayout):
    """Layout holding useful functions for list and search"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(self.children)
        Clock.schedule_once(self._assign_callbacks)

    def _assign_callbacks(self, _):
        for c in self.children:
            c.bind(on_release=lambda x: getattr(self, x.name)(x))


    @staticmethod
    def alphabetical(_):
        """Set sort order to A-Z"""
        with ItemCardContainer() as f:
            f.sort_type = 'item_name'
            f.sort_display()

    @staticmethod
    def group(_):
        """Set sort order to item group"""
        with ItemCardContainer() as f:
            f.sort_type = 'item_group'
            f.sort_display()

    @staticmethod
    def time(_):
        """Set sort order to time added"""
        with ItemCardContainer() as f:
            f.sort_type = 'creation'
            f.sort_display()

    @staticmethod
    def toggle_asc_desc(btn):
        """Change sort order to ascending or descending"""
        btn.icon = ({'sort-ascending', 'sort-descending'} - {btn.icon}).pop()
        btn.tooltip_text = ({"SwitchTo: Ascending", "SwitchTo: Descending"} - {btn.tooltip_text}).pop()
        with ItemCardContainer() as f:
            f.sort_desc = not f.sort_desc
            f.sort_display()

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
        with ItemCardContainer() as f:
            gro_list = f.convert_to_pool()
        Factory.SaveDialog(gro_list, MDApp.get_running_app().db).open()


class SearchBar(MDTextFieldRound):
    """Search for and add items from keyboard"""
