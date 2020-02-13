from operator import itemgetter

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tooltip import MDTooltip

from __init__ import hide_widget
from logical.state import ListState
from widget_sections.dialogs import DefaultsDialog


class ListScrollHelper(RelativeLayout):
    """Element background and scrollbar alignment"""
    pass


class ListScrollBar(ScrollView):
    """ScrollBar for list"""

    instance = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instance = self
        Clock.schedule_once(self._bar_width)

    def _bar_width(self, _):
        from widget_sections.selection import GroupScrollBar
        self.bar_width = GroupScrollBar.instance.bar_width


class ItemCardContainer(BoxLayout):
    """List preview displaying item cards"""

    instance = None
    sort_type = 'creation'

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        ItemCardContainer.instance = self

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def trigger_refresh(self):
        """Called when ListState is updated to signal a changed state"""
        self.height = ListState.instance.container_height


class ItemCard(MDCard):
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
        self.defaults_list = self.item.defaults.copy()
        self.defaults_list.sort(key=itemgetter(0))
        self.defaults_list = [str(num) for _, num in self.defaults_list]

        # set up animations and properties
        super().__init__(**kwargs)
        self._get_widget_refs()

        # create dropdown, set note text, item history
        self.defaults_dropdown = DropdownStack(self.defaults_list.copy(), self.amount)
        self.note_input.text = self.item.note

        self.expand_anim = Animation(size=(self.width, self.normal_height + self.expansion_height), duration=.12)
        self.expand_anim.bind(on_progress=lambda _, __, progress:
                         self._anim_progress(self.expansion_height, progress))
        self.expand_anim.bind(on_complete=lambda _, __: self._anim_complete())

        self.contract_anim = Animation(size=(self.width, self.normal_height), duration=.12)
        self.contract_anim.bind(on_progress=lambda _, __, progress:
                           self._anim_progress(-self.expansion_height, progress))
        self.contract_anim.bind(on_complete=lambda _, __: self._anim_complete())

    @property
    def toggle(self):
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
        self.node.height = self.normal_height + delta * progress
        ItemCardContainer.instance.trigger_refresh()

    def _anim_complete(self):
        """Update the stepped height of the container so the next animation uses new base value;
        Adjust widget visibility as animation is now complete
        """

        ListState.instance.anim_progress_delta = 0
        value = -1 if self.expanded else 1
        self.expanded = not self.expanded
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
        t = self.node.toggle
        ListState.instance.remove_card(self.node)
        if t:
            t.node = None

    def note_text_validate(self, text):
        """Set the note label visibility and text"""
        self.note_display.size_hint = (1, .2)
        self.note_display.text = text

    @property
    def item_name(self):
        """Used for sorting by name"""
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


class FloatingButton(MDFlatButton):
    """Floating values for defaults selection"""

    def __init__(self, value, **kwargs):
        self.pos_hint = {'center_x': .5, 'center_y': .6}
        super().__init__(**kwargs)
        self.text = value  # TODO
        if value == '':
            self.icon = 'minus-circle-outline'
        elif value == '+':
            self.icon = 'plus-circle-outline'
        else:
            self.icon = f'numeric-{value}-circle-outline'

    def on_release(self):
        if self.text == '+':
            return self.parent.parent.do_add_value()
        else:
            self.parent.parent.main_button.text = self.text
            self.parent.parent.dismiss()


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
            self.root.chevron.trigger_action(duration=.1)


class PreviewIconButton(MDIconButton, MDTooltip):
    """Larger icons and tooltip behavior"""

    def animation_tooltip_show(self, interval):
        if not self._tooltip:
            return
        (
                Animation(_scale_x=1, _scale_y=1, d=0.4)
                + Animation(opacity=1, d=0.4)
        ).start(self._tooltip)
