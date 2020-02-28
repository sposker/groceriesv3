"""Singleton Class that holds state of the list in progress; allows converting into work-in-progress pools,
formatted lists, updating database, etc. Manages order of cards in list.

Used in windows and android app. Access app has its own state.
"""

import time
from collections import deque

from kivymd.app import MDApp

from logical.pools_and_lists import ItemPool


class ItemNode:
    """Class `ItemNode` is responsible for managing the state of individual cards visible in the list container.
    This class passes information and instructions to widgets which in turn display that information.
    """

    all_nodes = set()

    def __init__(self, item=None, toggle=None, creation=None, note='', amount=None):

        self.item = item
        if toggle:
            toggle.graphics_toggle('down')
        self.toggle = toggle

        self._note = note
        _ = amount  # kwarg is present in certain loading situations so we can't remove it
        self.creation_time = creation if creation else time.time()

        self.prev = None
        self.next = None

        self.card = self.view_cls(self)
        self.amount = self.card.defaults_list[-1]
        self.card.height = self.view_cls.normal_height
        self._height = ListState.height_normal
        ItemNode.all_nodes.add(self)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return self.item == other.item if other else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.item.uid

    def __del__(self):
        ItemNode.all_nodes = ItemNode.all_nodes - {self}

    @property
    def is_expanded(self):
        return self.card.expanded

    @property
    def view_cls(self):
        return ListState.view_cls

    @property
    def item_name(self):
        return self.item.name.lower()

    @property
    def item_group(self):
        return self.item.group.uid

    @property
    def amount(self):
        if not self._amount:
            self._amount = self.card.defaults_list[-1]
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def note(self):
        if self._note is None:
            self._note = ''
        return self._note

    @note.setter
    def note(self, value):
        self._note = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        # self.card.size_hint_y = None
        self.card.height = self._height
        # self.card.canvas.ask_update()

    @property
    def list_fields(self):
        """Used for construction of list: Name, Number, Note"""
        return self.item, self.amount, self.note


class ContextList(deque):
    """`deque` subclass that manages order and provides references to cards in the container.
    Class `ContextList` handles administrative tasks associated with adding and sorting cards while the class
    `ListState` is responsible for the general state of the list and uses this class to manage it.
    """

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first = None
        self.last = None

        self._extra_height = 0

    def __enter__(self):
        """Store our current first and last values for later use"""
        self.pair = (self.first, self.last)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Adjust heights of first and last values based on MDSpec"""
        # if exc_type: TODO
        #     return None
        #
        # if self.prev_first == self.first:
        #     pass
        # else:
        #     if self.prev_first:
        #         self.prev_first.height = self.prev_first.height - 8
        #     if self.first:
        #         self.first.height = self.first.height + 8
        #
        # if self.prev_last == self.last:
        #     pass
        # else:
        #     if self.prev_last:
        #         self.prev_last.height = self.prev_last.height - 8
        #     if self.last:
        #         self.last.height = self.last.height + 8

        self.cards_container.trigger_refresh()
        self.pair = None

    @property
    def cards_container(self):
        return ListState.container


class ListState:
    """Reflects the state of the list in progress; accessed via MVC paradigm.
     The `ListState` singleton object is responsible for managing the state of the list as a whole.
    """

    instance = None
    container = None
    view_cls = None
    sort_desc = True

    sort_map = {
        'time': 'creation_time',
        'name': 'item_name',
        'group': 'item_group',
    }

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, low_spec=False):

        self.toggles_dict = {}

        self.normal_cards = 0
        self.expanded_cards = 0
        self.anim_progress_delta = 0

        self.app = MDApp.get_running_app()
        self.nodes_list = ContextList()
        self.sort_type = 'time'
        self.frozen_pool = None
        self.low_spec = low_spec

    @classmethod
    def values_from_card(cls, **kwargs):
        """Set certain values and definitions based on the card type used in the running app"""

    @property
    def height_normal(self):
        return self.view_cls.normal_height

    @property
    def height_expanded(self):
        return self.view_cls.normal_height + 60

    @property
    def container_height(self):

        # print('NORMAL:', self.normal_cards * self.height_normal)  # Normal cards)
        # print('EXPANDED', self.expanded_cards * self.height_expanded)   # Expanded cards)
        # print('SPACE', self.spacers * self.spacing)                  # spacers)
        # print('MDSPEC', min(16, len(self.linked_list) * 8))  # +8 on first and last for md spec)
        # print('ANIM', self.anim_progress_delta)

        return sum([
            self.normal_cards * self.height_normal,  # Normal cards
            self.expanded_cards * self.height_expanded,  # Expanded cards
            self.spacers * self.spacing,  # spacers
            # min(16, len(self.linked_list) * 8),  # +8 on first and last for md spec TODO
            self.anim_progress_delta  # Animation in progress
        ])

    @property
    def spacers(self):
        """Height created when spacing out cards"""
        return max(self.normal_cards + self.expanded_cards - 1, 0)

    @property
    def spacing(self):
        """Since container is None during `__init__`"""
        return self.container.spacing

    def clear(self):
        """Clear the list"""

        nodes = set(self.nodes_list)
        for node in nodes:
            try:
                node.toggle.do_toggle()
            except AttributeError:
                pass

        self.nodes_list.clear()
        self.container.clear_widgets()

    def add_card(self, card_node=None, sort=True, **kwargs):
        """Add a `ItemNode` to our `ContextList(), sort the list by default, and return the node"""
        if not card_node:
            card_node = ItemNode(**kwargs)

        with self.nodes_list as nl:
            nl.append(card_node)
            self.container.add_widget(card_node.card)

        self.normal_cards += 1
        if not self.low_spec and sort:
            self.sort_cards()

        return card_node

    def remove_card(self, node: ItemNode):
        """Delete a card from our list, adjusting state of `ToggleButton`, `WinItemCard`, and `self.nodes_list`."""

        with self.nodes_list as nl:

            if node.toggle:
                node.toggle.graphics_toggle('normal')
            nl.remove(node)
            self.container.remove_widget(node.card)

            if node.is_expanded:
                self.expanded_cards -= 1
            else:
                self.normal_cards -= 1

        del node

    @staticmethod
    def resize_card(node):
        node.card.resize()

    def anim_complete(self, value):
        self.normal_cards -= value
        self.expanded_cards += value
        self.container.trigger_refresh()

    @staticmethod
    def set_amount(node, value):
        node.amount = value

    @staticmethod
    def set_note(node, value):
        node.note = value

    def show_history(self, card):
        """TODO: history for item based on parsing previous lists"""

    def sort_cards(self):
        rev = not self.sort_desc
        sort = self.sort_map[self.sort_type]

        nodes_list = sorted(self.nodes_list, key=lambda n: getattr(n, sort), reverse=rev)

        with self.nodes_list as nl:
            self.container.clear_widgets()
            nl.clear()
            for next_node in nodes_list:
                self.container.add_widget(next_node.card)
            nl.extend(nodes_list)

    def request_pool_load(self):
        io = MDApp.get_running_app().io_manager
        pool = io.load_pool()
        if pool:
            self.populate_from_pool(pool)

    # noinspection PyUnboundLocalVariable
    def populate_from_pool(self, pool: ItemPool):
        """For loading an incomplete list back into the app"""
        for uid, info in pool.items():
            _, amount, note = info
            try:
                item = self.app.db.items[uid]
            except KeyError:
                toggle = None
                item = self.app.db.new_items[uid]
            else:
                toggle = self.toggles_dict[item.uid]
                toggle.graphics_toggle('down')
            finally:
                node = self.add_card(sort=False, item=item, toggle=toggle, amount=amount, note=note)
                if toggle:
                    toggle.node = node

        self.sort_cards()
        self.container.trigger_refresh()

    def convert_to_pool(self):
        """Convert preview items into ItemPool"""
        items = {node.list_fields for node in self.nodes_list}
        self.frozen_pool = ItemPool(items)
        return self.frozen_pool












