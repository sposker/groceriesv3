"""Singleton Class that holds state of the list in progress; allows converting into work-in-progress pools,
formatted lists, updating database, etc. Manages order of cards in list.

Used in windows and android app. Access app has its own state.
"""

import time

from kivymd.app import MDApp

from logical.pools_and_lists import ItemPool


class Node:
    """Node for linked list sorting"""

    all_nodes = set()

    def __init__(self, item=None, toggle=None, creation=None, note='', amount=None):

        self.item = item
        self.toggle = toggle

        self._note = note
        self._amount = amount if amount else ''
        self.creation_time = creation if creation else time.time()

        self.next = None
        self.prev = None

        self.card = self.view_cls(self)
        self.card.height = ListState.height_normal
        self._height = ListState.height_normal
        Node.all_nodes.add(self)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return self.item == other.item if other else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.item.uid

    @property
    def is_expanded(self):
        return self.card.expanded

    @property
    def view_cls(self):
        return ListState.view_cls

    @property
    def item_name(self):
        return self.item.name

    @property
    def item_group(self):
        return self.item.group.uid

    @property
    def amount(self):
        if self._amount is None:
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
        """Used for construction of list: Name, Group, Number, Note"""
        amount = self.amount if self.amount else None
        return self.item, amount, self.note


class DoubleLinkedList:
    """List of cards in the container"""

    def __init__(self):

        self.first = None
        self.last = None
        self.prev_first = None
        self.prev_last = None
        self._extra_height = 0

    def __enter__(self):
        """Store our current first and last values for later use"""
        self.prev_first = self.first
        self.prev_last = self.last

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Adjust heights of first and last values based on MDSpec"""
        if exc_type:
            print(exc_type, exc_tb, exc_val)
            return None

        if self.prev_first == self.first:
            pass
        else:
            if self.prev_first:
                self.prev_first.height = self.prev_first.height - 8
            if self.first:
                self.first.height = self.first.height + 8

        if self.prev_last == self.last:
            pass
        else:
            if self.prev_last:
                self.prev_last.height = self.prev_last.height - 8
            if self.last:
                self.last.height = self.last.height + 8

        print('prev_checks')
        # self.container.trigger_refresh()
        # self.prev_first = self.prev_last = None

    def __bool__(self):
        return self.first is self.last is None

    def __len__(self):
        length = 0
        current = self.first
        while current:
            length += 1
            current = current.next
        return length

    def __iter__(self):
        yield from self.get_node(range(len(self)))

    @property
    def container(self):
        return ListState.container

    def clear(self):
        self.first = None
        self.last = None
        Node.all_nodes = set()

    def get_node(self, index):
        current = self.first
        for i in range(index):
            if current is None:
                return None
            current = current.next
        return current

    def insert_after(self, ref_node, new_node):
        new_node.prev = ref_node
        if ref_node.next is None:
            self.last = new_node
        else:
            new_node.next = ref_node.next
            new_node.next.prev = new_node
        ref_node.next = new_node

    def insert_before(self, ref_node, new_node):
        new_node.next = ref_node
        if ref_node.prev is None:
            self.first = new_node
        else:
            new_node.prev = ref_node.prev
            new_node.prev.next = new_node
        ref_node.prev = new_node

    def insert_at_beg(self, new_node):
        if self.first is None:
            self.first = new_node
            self.last = new_node
        else:
            self.insert_before(self.first, new_node)

    def insert_at_end(self, new_node):
        if self.last is None:
            self.last = new_node
            self.first = new_node
        else:
            self.insert_after(self.last, new_node)

    def remove(self, node):
        if node.prev is None:
            self.first = node.next
        else:
            node.prev.next = node.next

        if node.next is None:
            self.last = node.prev
        else:
            node.next.prev = node.prev

    def show(self):
        print("______\nShow list data:")
        current_node = self.first
        while current_node is not None:
            print(current_node.prev.item if hasattr(current_node.prev, "item") else None, )
            print(current_node.item, current_node.card.height)
            print(current_node.next.item if hasattr(current_node.next, "item") else None)
            print('____')
            current_node = current_node.next
        print("*" * 50)
        # print(self.first.item, self.last.item)


class ListState:
    """Reflects the state of the list in progress; accessed via MVC paradigm. `Node` objects should be responsible
     for details of item cards whereas this class is responsible for the state of the list as a whole.
    """

    _instance = None
    container = None
    view_cls = None
    height_normal = 72
    height_expanded = height_normal + 60

    sort_map = {
        'time': 'creation_time',
        'name': 'item_name',
        'group': 'item_group',
    }

    def __init__(self):

        self.toggles_dict = {}

        self.normal_cards = 0
        self.expanded_cards = 0
        self.anim_progress_delta = 0

        self.app = MDApp.get_running_app()
        self.linked_list = DoubleLinkedList()
        self.sort_desc = True
        self.sort_type = 'time'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __enter__(self):
        """Convenience for accessing list state"""
        return self._instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.container.trigger_refresh()
        pass

    @property
    def container_height(self):

        # print('NORMAL:', self.normal_cards * self.height_normal)  # Normal cards)
        # print('EXPANDED', self.expanded_cards * self.height_expanded)   # Expanded cards)
        # print('SPACE', self.spacers * self.spacing)                  # spacers)
        # print('MDSPEC', min(16, len(self.linked_list) * 8))  # +8 on first and last for md spec)
        # print('ANIM', self.anim_progress_delta)

        return (
                self.normal_cards * self.height_normal +  # Normal cards
                self.expanded_cards * self.height_expanded +  # Expanded cards
                self.spacers * self.spacing +  # spacers
                min(16, len(self.linked_list) * 8) +  # +8 on first and last for md spec
                self.anim_progress_delta  # Animation in progress
        )

    @property
    def spacers(self):
        """Height created when spacing out cards"""
        return max(self.normal_cards + self.expanded_cards - 1, 0)

    @property
    def spacing(self):
        """Since container is None during `__init__`"""
        return self.container.spacing

    def add_card(self, card_node=None, **kwargs):
        """Create a new `Node` which in turn creates an `ItemCard`.
        Insert the new node into our `DoubleLinkedList` and add the card to our container.
        """
        if not card_node:
            card_node = Node(**kwargs)

        order = self.sort_map[self.sort_type]

        with self.linked_list:
            for i, node in enumerate(sorted(Node.all_nodes,
                                            key=lambda n: getattr(n, order),
                                            reverse=self.sort_desc)):
                # print(i, node)
                if node == card_node:
                    self.container.add_widget(card_node.card, index=i)
                    try:
                        self.linked_list.insert_before(self.linked_list.get_node(i), card_node)
                    except AttributeError:
                        self.linked_list.insert_at_end(card_node)
                    break
            self.normal_cards += 1

        return card_node

    def remove_card(self, node):
        """Delete a card from our list, adjusting state of `ToggleButton`, `ItemCard`, and `linked_list`."""
        Node.all_nodes = Node.all_nodes - {node}

        with self.linked_list:
            self.linked_list.remove(node)
            try:
                node.toggle.state = 'normal'
            except AttributeError:
                pass

            self.container.remove_widget(node.card)

            if node.is_expanded:
                self.expanded_cards -= 1
            else:
                self.normal_cards -= 1

        del node

    @staticmethod
    def resize_card(node):
        node.card.resize()

    def anim_complete(self, node, value):
        node.height = 132
        self.normal_cards -= value
        self.expanded_cards += value

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

        nodes = sorted(Node.all_nodes.copy(), key=lambda n: getattr(n, sort), reverse=rev)
        print(nodes)

        with self.linked_list:
            # self.linked_list.clear()
            self.container.clear_widgets()
            for n in nodes:
                self.linked_list.remove(n)
            while nodes:
                next_node = nodes.pop()
                print(next_node)
                self.linked_list.insert_at_end(next_node)
                self.container.add_widget(next_node.card)
            print('outside while, inside list context')
        print('outside list context, inside sort')

    def populate_from_pool(self, pool: ItemPool):
        """For loading an incomplete list back into the app"""
        for uid, info in pool.items():
            _, amount, note = info
            try:
                item = self.app.db.items[uid]
            except KeyError:
                item = self.app.db.new_items[uid]
                toggle = None
            else:
                toggle = self.toggles_dict[item.uid]
                toggle.state = 'down'
                toggle.graphics_toggle()
            finally:
                # noinspection PyUnboundLocalVariable
                self.add_card(item=item, toggle=toggle, amount=amount, note=note)

    def convert_to_pool(self):
        """Convert preview items into ItemPool"""
        items = {n.list_fields for n in self.linked_list}
        return ItemPool(items)
