"""Preview widgets which display a list in progress-- VIEW in the MVC paradigm"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.dropdown import DropDown
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tooltip import MDTooltip

from __init__ import hide_widget
from logical.state import ListState
from widget_sections.dialogs import DefaultsDialog
from widget_sections.shared_preview import ItemCardContainer


class WinItemCard(MDCard):
    """Item Preview Widget"""

    normal_height = 72
    expansion_height = 60
    expanded = False
    visible = {'amount',
               'chevron',
               'item_title',
               }

    """
    For whatever reason, the widgets in `_hidden_at_start` don't play well with the function `hide_widget`. This has
    resulted in a non-deterministic bug that doesn't make much sense to begin with. Therefore the attributes are
    hard-coded into the class and accessed when resizing the cards. To change the attributes of widgets shown when
    expanding the card, simply edit these values. If you add a new widget to the expansion, include it here.
    """

    _hidden_at_start = {
        'expansion': (48.0, None, 1.0, False),
        'history': (60, None, 1.0, True),
        'delete_card': (34.0, 1, 1.0, False),
        'note_input': (48.0, None, 1.0, False),
    }

    def __init__(self, node, **kwargs):
        # simple item properties
        self.node = node

        # work with item defaults list
        self.defaults_pairs = sorted(self.item.defaults.copy(), key=lambda d: d[0])
        self.defaults_list = [str(num) for _, num in self.defaults_pairs]

        # set up animations and properties
        super().__init__(**kwargs)
        self._get_widget_refs()

        # create dropdown, set note text, item history
        self.defaults_dropdown = DropdownStack(self.defaults_list.copy(), self.amount)
        self.note_input.text = self.item.note

        self.expand_anim = Animation(size=(self.width, self.normal_height + self.expansion_height), duration=.12)
        self.expand_anim.bind(on_progress=lambda a_, b_, progress:
        self._anim_progress(self.expansion_height, progress))
        self.expand_anim.bind(on_complete=lambda a_, b_: self._anim_complete())

        self.contract_anim = Animation(size=(self.width, self.normal_height), duration=.12)
        self.contract_anim.bind(on_progress=lambda a_, b_, progress:
        self._anim_progress(-self.expansion_height, progress))
        self.contract_anim.bind(on_complete=lambda a_, b_: self._anim_complete())

        self.color_anim = Animation(text_color=MDApp.get_running_app().text_color, duration=1, t='in_expo')

    @property
    def toggle(self):
        """This is a reference to a toggle button in the selection part of the app-- NOT a function"""
        return self.node.toggle

    @property
    def item(self):
        return self.node.item

    def _get_widget_refs(self):
        """Get reference to buttons/menus via name attribute; skip widgets without names"""
        for name, child in self.ids.items():
            if name in self._hidden_at_start:
                child.saved_attrs = True
                child.height, child.size_hint[1], child.opacity, child.disabled = 0, None, 0, True

    def _make_hidden(self):
        for attr, values in self._hidden_at_start.items():
            child = getattr(self, attr)
            if child.saved_attrs:
                child.height, child.size_hint[1], child.opacity, child.disabled = values
            else:
                if not (child.name == 'note_input' and child.text):
                    child.height, child.size_hint[1], child.opacity, child.disabled = 0, None, 0, True

            child.saved_attrs = not child.saved_attrs

    def _anim_progress(self, delta, progress):
        """Increment the size of card and container"""

        ListState.instance.anim_progress_delta = delta * progress
        if self.expanded:
            self.node.height = self.expansion_height + self.normal_height + delta * progress
        else:
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

    def _resize(self):
        ListState.instance.resize_card(self.node)

    def resize(self):
        if not self.expanded:
            self.chevron.icon = 'chevron-up'
            self.expand_anim.start(self)
        else:
            self.chevron.icon = 'chevron-down'
            self.contract_anim.start(self)

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


class DropdownStack(DropDown):
    """Stacked default buttons"""

    orientation = 'vertical'
    spacing = dp(4)

    def __init__(self, defaults, main_btn, **kwargs):
        super().__init__(**kwargs)
        self.main_button = main_btn
        self.widgets = [FloatingButton(v) for v in defaults]

        self.widgets.append(FloatingButton('+'))

        for w in self.widgets:
            w.root_ = main_btn.root
            w.stack_ = self
            self.add_widget(w)

    def open(self, widget):
        """Hide redundant dropdown option"""
        super().open(widget)
        for btn in self.widgets:
            if btn.text == widget.text:
                hide_widget(btn)
            else:
                hide_widget(btn, dohide=False)

    def do_add_value(self):
        self.dismiss()
        dialog = DefaultsDialog(self.main_button)
        dialog.open()


class DefaultsButton(MDFlatButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expanded = False


class NoteInput(MDTextField):
    """Input for item note"""

    def on_text_validate(self):
        """Show note label and collapse the card"""
        if self.text:
            self.root.note_text_validate(self.text)
            self.root.chevron.trigger_action(duration=.1)  # simulate a touch down on the chevron


class PreviewIconButton(MDIconButton, MDTooltip):
    """Larger icons and tooltip behavior"""

    def animation_tooltip_show(self, interval):
        if not self._tooltip:
            return
        (
                Animation(_scale_x=1, _scale_y=1, d=0.4)
                + Animation(opacity=1, d=0.4)
        ).start(self._tooltip)


class FloatingButton(MDFlatButton):
    """Floating values for defaults selection"""

    def __init__(self, value, **kwargs):
        self.pos_hint = {'center_x': .5, 'center_y': .6}
        super().__init__(**kwargs)
        self.text = value
        if value == '+':
            self.icon = 'plus-circle-outline'
        else:
            self.icon = f'numeric-{value}-circle-outline'

    def on_release(self):
        if self.text == '+':
            return self.parent.parent.do_add_value()
        else:
            self.root_.amount.text = self.text
            self.root_.node.amount = self.text
            self.stack_.dismiss()
