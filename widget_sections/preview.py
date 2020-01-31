from collections import deque
from operator import itemgetter

from kivy.clock import Clock
from kivy.properties import OptionProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.list import TwoLineRightIconListItem
from kivymd.uix.menu import MDDropdownMenu

from logical.stores import ShoppingList
from logical import hide_widget
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
    state = OptionProperty('creation', options=['item_group', 'creation', 'item_name'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_node = self.final_node = None

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

    def add_card(self, item, creation_time):
        """Add a item to the preview via toggle button"""
        card = ItemCard(item, creation_time)
        self.adjust_height(card._height)
        self.add_widget(card)
        print(self.height, 'added')
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

    def construct_list(self):
        """Convert preview items into actual list"""
        items = {w.list_fields for w in self.children}
        return ShoppingList(items)

    def remove_card(self, card):
        """Remove an item from the preview"""
        self.adjust_height(-card.height)
        self.remove_widget(card)
        print(self.height, 'removed')

    def sort_display(self, prop: str):
        """Called with name of card attributes"""
        pairs = [getattr((widget, prop), widget) for widget in self.children]
        ordered = sorted(pairs, key=itemgetter[0])
        self.clear_widgets()
        for pair in ordered:
            self.add_widget(pair[1])
        self.state = prop


class ItemCard(MDCard):
    """Item Preview Widget"""

    _height = 72
    _expansion_height = 60
    state = False
    names = {'amount',
             'chevron',
             'expansion',
             'history',
             'delete_card',
             'note_input',
             }

    def __init__(self, item, creation_time, **kwargs):
        self.item = item
        self._creation = creation_time
        self.note = ''
        super().__init__(**kwargs)
        self._get_widget_refs()

        def random_icon():
            import random
            i = random.randint(0, 10)
            return str(i)

        self.amount.text = random_icon()

    def _get_widget_refs(self):
        """Get reference to buttons/menus via name attribute; skip widgets without names"""
        for child in self.walk(restrict=True):
            try:
                name = getattr(child, 'name')
            except AttributeError:
                pass
            else:
                print(name)
                self.__dict__[name] = child

            try:
                name = getattr(child.parent, 'name')
            except AttributeError:
                pass
            else:
                if name == 'expansion':
                    hide_widget(child)

    def expand(self):
        print('expand', self.chevron)
        self.chevron.icon = 'chevron-up'
        with ItemCardContainer() as f:
            f.adjust_height(self._expansion_height, offset=0)
            self.height += self._expansion_height
            self._expansion.height = self._expansion_height
            self._expansion.opacity = 1

    def contract(self):
        print('contract', self.amount)
        self.chevron.icon = 'chevron-down'
        with ItemCardContainer() as f:
            f.adjust_height(-self._expansion_height, offset=0)
            self.height -= self._expansion_height
            self._expansion.height = 0
            self._expansion.opacity = 0

    def move(self, state):
        if state:
            return self.expand()
        else:
            return self.contract()

    @property
    def creation(self):
        """Used for sorting"""
        return self._creation

    @property
    def item_name(self):
        """Used for sorting"""
        return self.item.name

    @property
    def item_group(self):
        """Used for sorting"""
        return self.item.group.name

    @property
    def list_fields(self):
        """Used for construction of list: Name, Group, Number, Note"""
        return self.item_name, self.item_group, self.amount.text, self.note


class ItemExpanded(BoxLayout):
    """Expanded list preview widget, allows editing"""

    def __init__(self, parent, **kwargs):
        self.item = parent.item
        super().__init__(**kwargs)

    def populate(self):
        ...


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
