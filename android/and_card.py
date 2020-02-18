from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField

from android.screens import DetailsScreen
from logical.state import ListState
from widget_sections.shared_preview import ItemCardContainer


class AndroidItemCard(MDCard):
    """Item Preview Widget for mobile"""

    normal_height = 144
    expanded = False

    def __init__(self, node, **kwargs):
        # simple item properties
        self.node = node

        # work with item defaults list
        self.defaults_pairs = sorted(self.item.defaults.copy(), key=lambda d: d[0])

        self.defaults_list = [str(num) for _, num in self.defaults_pairs]

        # set up animations and properties
        super().__init__(**kwargs)

    @property
    def toggle(self):
        """This is a reference to a toggle button in the selection part of the app-- NOT a function"""
        return self.node.toggle

    @property
    def item(self):
        return self.node.item

    def show_details(self):
        sm = MDApp.get_running_app().manager
        s = DetailsScreen(self)
        s.add_defaults(self.defaults_list)
        sm.transition.direction = 'left'
        sm.add_widget(s)
        sm.current = 'details'

    @staticmethod
    def open_defaults_dialog(btn):
        Factory.DefaultsDialog(btn).open()

    def kvlang_remove_card(self):
        """Called from card's delete button"""
        t = self.node.toggle  # get a reference to toggle button now, because we are about to delete the node
        ListState.instance.remove_card(self.node)
        if t:  # If it was a new item, there is no toggle button associated with the card or node
            t.node = None

    def note_text_validate(self, text):
        """Set the note label visibility and text"""
        self.note_display.size_hint = (1, .2)
        self.note_display.text = text
        self.node.note = text

    @property
    def item_name(self):
        """Used in kvlang"""
        return self.item.name


class FloatingButton(MDFlatButton,):
    """Toggle button for details screen"""

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.text = value
        self.state = 'normal'

    def on_release(self):

        for button in self.parent.children:
            if button is self:
                self.text_color = MDApp.get_running_app().theme_cls.accent_color
                self.state = 'down'
            else:
                button.text_color = MDApp.get_running_app().text_color
                button.state = 'normal'

        if self.text == "+":
            return self.do_add_value()

    def do_add_value(self):
        btn = self.parent.root_.card.amount
        Factory.DefaultsDialog(btn, floating_btn=self).open()


class DefaultsOptions(BoxLayout):
    """Buttons for picking defaults"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NoteInput(MDTextField):
    """Input for item note"""


class PreviewIconButton(MDIconButton):
    """Larger icons and tooltip behavior"""

