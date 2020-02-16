from kivy.animation import Animation
from kivy.clock import Clock
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
        print(self.defaults_list)

        # set up animations and properties
        super().__init__(**kwargs)

        # self.expand_anim = Animation(size=(self.width, self.normal_height + self.expansion_height), duration=.12)
        # self.expand_anim.bind(on_progress=lambda a_, b_, progress:
        #                       self._anim_progress(self.expansion_height, progress))
        # self.expand_anim.bind(on_complete=lambda a_, b_: self._anim_complete())
        #
        # self.contract_anim = Animation(size=(self.width, self.normal_height), duration=.12)
        # self.contract_anim.bind(on_progress=lambda a_, b_, progress:
        #                         self._anim_progress(-self.expansion_height, progress))
        # self.contract_anim.bind(on_complete=lambda a_, b_: self._anim_complete())

    @property
    def toggle(self):
        """This is a reference to a toggle button in the selection part of the app-- NOT a function"""
        return self.node.toggle

    @property
    def item(self):
        return self.node.item

    def _anim_progress(self, delta, progress):
        """Increment the size of card and container"""

        ListState.instance.anim_progress_delta = delta * progress
        self.node.height = self.normal_height + delta * progress
        ItemCardContainer.instance.trigger_refresh()

    def _anim_complete(self):
        """Update the stepped height of the container so the next animation uses new base value;
        Adjust widget visibility as animation is now complete;
        Focus the note input widget.
        """

        ListState.instance.anim_progress_delta = 0
        value = -1 if self.expanded else 1
        self.expanded = not self.expanded
        if self.expanded:
            Clock.schedule_once(lambda _: setattr(self.note_input, 'focus', True), .1)
        ListState.instance.anim_complete(value)
        return self._make_hidden()

    def show_details(self):
        sm = MDApp.get_running_app().manager
        s = DetailsScreen(self)
        s.add_defaults(self.defaults_list)
        sm.transition.direction = 'left'
        sm.add_widget(s)
        sm.current = 'details'

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

    @property
    def item_name(self):
        """Used in kvlang"""
        return self.item.name


class FloatingButton(MDFlatButton, ToggleButtonBehavior):
    """Toggle button for details screen"""

    group = ObjectProperty(None, allownone=True)

    def __init__(self, value, **kwargs):
        self.group = 'defaults_toggles'
        super().__init__(**kwargs)
        self.text = value
        try:
            self.icon = f'numeric-{int(value)}-circle-outline'
        except ValueError:
            self.icon = 'roman-numeral-10'

    def on_state(self, _, value):
        if value == 'down':
            self.text_color = MDApp.get_running_app().theme_cls.accent_color
        else:
            self.text_color = MDApp.get_running_app().text_color


class DefaultsOptions(BoxLayout):
    """Buttons for picking defaults"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class NoteInput(MDTextField):
    """Input for item note"""


class PreviewIconButton(MDIconButton):
    """Larger icons and tooltip behavior"""

