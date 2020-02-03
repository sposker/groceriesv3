from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp

from kivymd.uix.textfield import MDTextFieldRound

from widget_sections.preview import ItemCardContainer


class ListFunctionsBar(BoxLayout):
    """Layout holding useful functions for list and search"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(self.children)
        Clock.schedule_once(self._assign_callbacks)

    def _assign_callbacks(self, _):
        for c in self.children:
            c.bind(on_release=lambda x: getattr(self, x.name)(x))

    def alphabetical(self, *_):
        """Set sort order to A-Z"""
        with ItemCardContainer() as f:
            f.sort_type = 'item_name'
            f.sort_display()

    def group(self, *_):
        """Set sort order to item group"""
        with ItemCardContainer() as f:
            f.sort_type = 'item_group'
            f.sort_display()

    def time(self, *_):
        """Set sort order to time added"""
        with ItemCardContainer() as f:
            f.sort_type = 'creation'
            f.sort_display()

    def toggle_asc_desc(self, btn):
        """Change sort order to ascending or descending"""
        btn.icon = ({'sort-ascending', 'sort-descending'} - {btn.icon}).pop()
        with ItemCardContainer() as f:
            f.sort_desc = not f.sort_desc
            f.sort_display()

    def reset(self, *_):
        """Clear the list"""
        with ItemCardContainer() as f:
            children = f.children.copy()
            for card in children:
                f.remove_card(card)

    def save(self, btn):
        """Launch the save dialog"""
        with ItemCardContainer() as f:
            gro_list = f.construct_grocery_list()
        Factory.SaveDialog(gro_list, MDApp.get_running_app().db).open()


class SearchBar(MDTextFieldRound):
    """Search for and add items from keyboard"""
