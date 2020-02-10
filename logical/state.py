"""Singleton Class that holds state of the list in progress; allows converting into work-in-progress pools,
formatted lists, updating database, etc. Manages order of cards in list.

Used in windows and android app. Access app has its own state.
"""
from logical.pools_and_lists import ItemPool


class Node:
    """Node for linked list sorting"""

    def __init__(self, data=None):
        self.data = data
        self.next = None
        self.prev = None


class DoubleLinkedList:
    """List of cards in the container"""

    def __init__(self):
        self.first = None
        self.last = None

    def __len__(self):
        length = 0
        current = self.first
        while current:
            length += 1
            current = current.next
        return length

    def __iter__(self):
        yield from self.get_node(range(len(self)))

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


class ListState:

    _instance = None
    height_normal = 72
    height_expanded = height_normal + 60

    def __init__(self):

        self.container = None
        self.view_cls = None

        self.normal_cards = 0
        self.expanded_cards = 0

        self.items = DoubleLinkedList()
        self.sort_dir = 'descending'
        self.sort_type = 'added'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def container_height(self):
        return (self.normal_cards * self.height_normal +
                self.expanded_cards * self.height_expanded +
                self.spacers * self.spacing
                ) + min(16, len(self.items)*8)  # Cards + spacers, then +8 on first and last for md spec

    @property
    def spacers(self):
        """Height created when spacing out cards"""
        return self.normal_cards + self.expanded_cards - 1

    @property
    def spacing(self):
        return self.container.spacing

    def add_card(self):
        """
        self.container.add (self.view_cls(item)??????
        :return:
        """

    def remove_card(self):
        ...

    def sort_cards(self, sort_by):
        ...

    def populate_from_pool(self, pool: ItemPool):
        """Create cards from pool of items"""

    def convert_to_pool(self):
        """Convert preview items into ItemPool"""
        items = {w.data.list_fields for w in self.items}
        return ItemPool(items)
