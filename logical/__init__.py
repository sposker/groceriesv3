class UIDRoot:
    """Comparison and hash values for objects with uids (Group, Item, Location)"""

    uid = None

    def __ge__(self, other):
        return str.__ge__(self.uid, other.uid)

    def __le__(self, other):
        return str.__ge__(self.uid, other.uid)

    def __gt__(self, other):
        return str.__gt__(self.uid, other.uid)

    def __lt__(self, other):
        return str.__lt__(self.uid, other.uid)

    def __eq__(self, other):
        if self.uid == other:
            return True
        try:
            if self.uid == other.uid:
                return True
        except (AttributeError, ValueError):
            pass

    def __hash__(self):
        return hash(self.__repr__())
