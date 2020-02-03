class Node:
    """A node in a doubly-linked list."""
    def __init__(self, data=None, prev=None, next=None, sort_data=None):
        self.data = data
        self.prev = prev
        self.next = next
        self.sort_data = sort_data

    def __gt__(self, other):
        return str.__gt__(self.sort_data, other.sort_data)

    def __eq__(self, other):
        return str.__eq__(self.sort_data, other.sort_data)

    def __repr__(self):
        return repr(self.data)

    def __hash__(self):
        return hash(self.data)


class DoublyLinkedList:
    """Implementation of DLL for use in list preview-- used for efficient sorting and insertion"""

    def __init__(self):
        """Create a new doubly linked list. Takes O(1) time."""
        self.head = None

    def __str__(self):
        """Return a string representation of the list. Takes O(n) time."""
        nodes = []
        curr = self.head
        while curr:
            nodes.append(repr(curr))
            curr = curr.next
        return '[' + ', '.join(nodes) + ']'

    def prepend(self, data):
        """Insert a new element at the beginning of the list. Takes O(1) time."""
        new_head = Node(data=data, next=self.head)
        if self.head:
            self.head.prev = new_head
        self.head = new_head

    def append(self, data):
        """Insert a new element at the end of the list. Takes O(n) time."""
        if not self.head:
            self.head = Node(data=data)
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = Node(data=data, prev=curr)

    def find(self, key):
        """Search for the first element with `data` matching `key`.
        Return the element or `None` if not found. Takes O(n) time.
        """
        curr = self.head
        while curr and curr.data != key:
            curr = curr.next
        return curr  # Will be None if not found

    def remove_elem(self, node):
        """Unlink an element from the list. Takes O(1) time."""
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if node is self.head:
            self.head = node.next
        node.prev = None
        node.next = None

    def remove(self, key):
        """Remove the first occurrence of `key` in the list. Takes O(n) time."""
        elem = self.find(key)
        if not elem:
            return
        self.remove_elem(elem)

    def reverse(self):
        """Reverse the list in-place. Takes O(n) time."""
        curr = self.head
        prev_node = None
        while curr:
            prev_node = curr.prev
            curr.prev = curr.next
            curr.next = prev_node
            curr = curr.prev
        self.head = prev_node.prev
