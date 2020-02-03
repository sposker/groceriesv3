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

from logical import hide_widget
from logical.doubly_linked_list import Node, DoublyLinkedList
from logical.stores import ShoppingList, ItemPool

# from widget_sections.selection import GroupScrollBar


# class LPDNumberInput(TextInput):
#
#     ...
#
#
# class LPNoteInput(TextInput):
#
#     ...
#
#
# class OptionsButton(ButtonBehavior, Image):
#
#     ...
#
#
# class DefaultsDropdownButton(Button):
#
#     ...
#
#
# class LPDContainer(GridLayout):
#     cols = 1
#
#
from windows.dialogues import DefaultsDialog


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
        self.dl_list = DoublyLinkedList()

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

    def add_card(self, toggle, creation_time, nfo=None):
        """Add a item to the preview via toggle button"""
        if toggle is None:  # TODO: Handle new item
            nfo()
            ...
        card = ItemCard(toggle, creation_time)
        self.adjust_height(card.default_height)
        self.stepped_height += card.default_height + self.spacing
        self.add_widget(card)
        print(self.height, self.stepped_height, 'added')
        return card

    # TODO: First/Last widget +8 dp for MD spec
    # def add_widget(self, widget, index=0, canvas=None):
    #     if not self.children:
    #         self.init_node = widget
    #     super().add_widget(widget, index=0, canvas=None)
    #     if self.final_node:
    #         self.final_node.height = widget.height
    #     self.final_node = widget
    #     widget.height += 8

    def construct_grocery_list(self):
        """Convert preview items into actual list"""
        items = {w.list_fields for w in self.children}
        pool = ItemPool(items)
        return ShoppingList(pool, MDApp.get_running_app().db.stores['default'])

    def remove_card(self, card):
        """Remove an item from the preview"""
        if card.toggle.state == 'down':  # called from card's delete button rather than from toggle itself
            return card.toggle.menu_delete()

        self.adjust_height(-card.height)
        self.stepped_height -= (card.height + self.spacing)
        self.remove_widget(card)
        print(self.height, self.stepped_height, 'removed')

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
    _hidden_at_start = {'expansion',
                        'history',
                        'delete_card',
                        'note_input',
                        }

    def __init__(self, toggle, creation_time, **kwargs):
        # simple item properties
        self.toggle = toggle
        self.item = toggle.item
        self._creation = creation_time
        self.note = ''
        self.node = None

        # work with item defaults list
        self.defaults_list = self.item.defaults.copy()
        self.defaults_list.sort(key=itemgetter(0))
        self.defaults_list = [str(num) for _, num in self.defaults_list]

        # set up animations and properties
        super().__init__(**kwargs)
        self._get_widget_refs()
        self._make_animations()

        # create dropdown
        self.defaults_dropdown = DropdownStack(self.defaults_list.copy(), self.amount)

    def _make_animations(self):
        eh = self._expansion_height

        self.expand_anim = Animation(size=(self.width, self.default_height + eh), duration=.12)
        self.expand_anim.bind(on_progress=lambda _, __, progress: self._anim_progress(eh, progress))
        self.expand_anim.bind(on_complete=lambda _, __: self._anim_complete(eh, False))

        self.contract_anim = Animation(size=(self.width, self.default_height), duration=.12)
        self.contract_anim.bind(on_progress=lambda _, __, progress: self._anim_progress(-eh, progress))
        self.contract_anim.bind(on_complete=lambda _, __: self._anim_complete(-eh, True))

    def _get_widget_refs(self):
        """Get reference to buttons/menus via name attribute; skip widgets without names"""
        for child in self.walk(restrict=True):
            try:
                name = getattr(child, 'name')
            except AttributeError:
                pass
            else:
                self.__dict__[name] = child

        self._make_hidden()
        # TODO: widgets disabled on expand
        # TODO: Try manually creating saved attrs for widgets to work with function 'hide_widget'

    def _make_hidden(self, dohide=True):
        for attr in self._hidden_at_start:
            child = getattr(self, attr)
            hide_widget(child, dohide=dohide)

    def _adjust_widgets(self):
        self.primary.remove_widget(self.defaults_floater)
        self.primary.remove_widget(self.chevron)
        self.primary.add_widget(self.chevron, index=3)
        self.primary.add_widget(self.defaults_floater, index=2)

    def _anim_progress(self, delta, progress):
        """Increment the size of card and container"""

        with ItemCardContainer() as f:
            f.height = f.stepped_height + round(delta*progress)
        self.expansion.height = self.default_height + round(delta * progress)

    def _anim_complete(self, increment, dohide):
        """Update the stepped height of the container so the next animation uses new base value;
        Adjust widget visibility as animation is now complete
        """

        with ItemCardContainer() as f:
            f.stepped_height += increment
        return self._make_hidden(dohide=dohide)

    def move(self):
        if not self.expanded:
            self.chevron.icon = 'chevron-up'
            self.expand_anim.start(self)
        else:
            self.chevron.icon = 'chevron-down'
            self.contract_anim.start(self)
        self.expanded = not self.expanded

    def kvlang_remove_card(self):
        with ItemCardContainer() as f:
            f.remove_card(self)
            ...

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
        return self.item, amount, self.note


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

    # def display_values(self):
    #     if not self.expanded:
    #         stack = DropdownStack(self.root.defaults_list.copy(), self)
    #         self.root.primary.add_widget(stack)
    #         self.expanded = True

# class ListFunctionsBar(GridLayout):
#     pass
#
#
# class ListFunctionsButton(ToggleButtonBehavior, Image):
#
#     def toggle(self, btn_id):
#         if self.state == 'down':
#             redraw_canvas(self, ELEMENT_COLOR)
#             ListPreview.instance.do_sort(btn_id)
#         else:
#             redraw_canvas(self, BACKGROUND_COLOR)
#

# class SearchBar(TextInput):
#     def on_parent(self, *_):
#         self.focus = True
#
#
# class SearchWidget(BoxLayout):
#     pass
