import time
from operator import itemgetter

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import OptionProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDInputDialog
from kivymd.uix.list import TwoLineRightIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.tooltip import MDTooltip

from logical import hide_widget
from logical.items import GroceryItem
from logical.pools_and_lists import ItemPool, ShoppingList

from windows.dialogs import DefaultsDialog


class DefaultsDropdown(MDDropdownMenu):
    ...


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

    _instance = None
    sort_type = 'creation'
    sort_desc = True
    stepped_height = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __enter__(self):
        return self._instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def adjust_height(self, h, offset=None):
        offset = self.spacing if offset is None else offset
        if h > 0:
            h += offset
        else:
            h -= offset
        self.height = self.height + h

    def add_card(self, toggle=None, item=None):
        """Add a item to the preview via toggle button"""
        card = ItemCard(toggle=toggle, item=item)
        self.adjust_height(card.default_height)
        self.stepped_height += (card.default_height + self.spacing)
        self.add_widget(card)
        # print(self.height, self.stepped_height, 'added')
        return card

    def dialog_add_card(self, info: dict):
        """Add a card for a new item via AddItemDialog"""
        db = MDApp.get_running_app().db
        item = db.add_new_item(info)
        self.add_card(item=item)

    # TODO: First/Last widget +8 dp for MD spec
    # def add_widget(self, widget, index=0, canvas=None):
    #     if not self.children:
    #         self.init_node = widget
    #     super().add_widget(widget, index=0, canvas=None)
    #     if self.final_node:
    #         self.final_node.height = widget.height
    #     self.final_node = widget
    #     widget.height += 8

    def populate_from_pool(self, pool: ItemPool):
        """Create cards from pool of items"""

    def convert_to_pool(self):
        """Convert preview items into ItemPool"""
        items = {w.list_fields for w in self.children}
        return ItemPool(items)

    def remove_card(self, card):
        """Remove an item from the preview"""
        try:
            if card.toggle.state == 'down':
                return card.toggle.menu_delete()
        except AttributeError:  # Card with no associated toggle button
            pass

        self.adjust_height(-card.height)
        self.stepped_height -= (card.height + self.spacing)
        self.remove_widget(card)
        # print(self.height, self.stepped_height, 'removed')

    def sort_display(self):
        """Called with name of card attributes"""
        prop = self.sort_type
        pairs = [(getattr(widget, prop), widget) for widget in self.children]
        ordered = sorted(pairs, key=itemgetter(0))
        if self.sort_desc:
            ordered.reverse()
        self.clear_widgets()
        for pair in ordered:
            self.add_widget(pair[1])


class ItemCard(MDCard):
    """Item Preview Widget"""

    default_height = 72
    _expansion_height = 60
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
        'history': (60, None, 1.0, False),
        'delete_card': (34.0, 1, 1.0, False),
        'note_input': (48.0, None, 1.0, False),
    }

    def __init__(self, toggle=None, item=None, **kwargs):
        # simple item properties
        self.toggle = toggle
        self.item = toggle.item if toggle else item  # No toggle button for new items
        self._creation = time.time()

        # work with item defaults list
        self.defaults_list = self.item.defaults.copy()
        self.defaults_list.sort(key=itemgetter(0))
        self.defaults_list = [str(num) for _, num in self.defaults_list]

        # set up animations and properties
        super().__init__(**kwargs)
        self._get_widget_refs()

        # create dropdown, set note text, item history  #TODO history
        self.defaults_dropdown = DropdownStack(self.defaults_list.copy(), self.amount)
        self.note_input.text = self.item.note

    @property
    def expand_anim(self):
        eh = self._expansion_height

        expand_anim = Animation(size=(self.width, self.default_height + eh), duration=.12)
        expand_anim.bind(on_progress=lambda _, __, progress: self._anim_progress(eh, progress))
        expand_anim.bind(on_complete=lambda _, __: self._anim_complete(eh))

        return expand_anim

    @property
    def contract_anim(self):
        eh = self._expansion_height

        contract_anim = Animation(size=(self.width, self.default_height), duration=.12)
        contract_anim.bind(on_progress=lambda _, __, progress: self._anim_progress(-eh, progress))
        contract_anim.bind(on_complete=lambda _, __: self._anim_complete(-eh))

        return contract_anim

    def _get_widget_refs(self):
        """Get reference to buttons/menus via name attribute; skip widgets without names"""
        for child in self.walk(restrict=True):
            try:
                name = getattr(child, 'name')
            except AttributeError:
                pass
            else:
                self.__dict__[name] = child

                if child.name in self._hidden_at_start:
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

        with ItemCardContainer() as f:
            f.height = f.stepped_height + round(delta * progress)
        self.expansion.height = self.default_height + round(delta * progress)

    def _anim_complete(self, increment):
        """Update the stepped height of the container so the next animation uses new base value;
        Adjust widget visibility as animation is now complete
        """

        with ItemCardContainer() as f:
            f.stepped_height += increment
        return self._make_hidden()

    def move(self):
        if not self.expanded:
            self.chevron.icon = 'chevron-up'
            self.expand_anim.start(self)
        else:
            self.chevron.icon = 'chevron-down'
            self.contract_anim.start(self)
        self.expanded = not self.expanded

    def kvlang_remove_card(self):
        """Called from card's delete button"""
        with ItemCardContainer() as f:
            f.remove_card(self)

    def note_text_validate(self, text):
        """Set the note label visibility and text"""
        self.note_display.size_hint = (1, .2)
        self.note_display.text = text

    @property
    def creation(self):
        """Used for sorting by creation time"""
        return self._creation

    @property
    def item_name(self):
        """Used for sorting by name"""
        return self.item.name

    @property
    def item_group(self):
        """Used for sorting by group"""
        return self.item.group.name

    @property
    def list_fields(self):
        """Used for construction of list: Name, Group, Number, Note"""
        try:
            amount = int(self.amount.text)
        except ValueError:
            amount = None
        return self.item, amount, self.note_display.text


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

    # def on_focus(self, _, value):
    #     if not value and self.text:
    #         return self.on_text_validate()

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
