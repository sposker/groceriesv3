import time


class DisplayGroup:
    """Grouping items for display"""
    _names = {}
    _uids = {}

    def __init__(self, name, uid=None):
        self.name = name

        if not uid:
            self.uid = 'g' + str(len(self._names)).zfill(2)
        elif 'g' in str(uid):
            self.uid = uid
        else:
            self.uid = 'g' + str(uid).zfill(2)

        DisplayGroup._names[self.name] = self
        DisplayGroup._uids[self.uid] = self

    def __ge__(self, other):
        return str.__ge__(self.uid, other.uid)

    def __le__(self, other):
        return str.__ge__(self.uid, other.uid)

    def __gt__(self, other):
        return str.__gt__(self.uid, other.uid)

    def __lt__(self, other):
        return str.__lt__(self.uid, other.uid)

    def __eq__(self, other):
        if self.uid == other.uid:
            return True

    def __hash__(self):
        return hash(self.uid)


class GroceryItem:

    _uids = set()

    def __init__(self,
                 name,
                 group=None,
                 defaults=None,
                 note=None,
                 uid=None,
                 ):

        self.name = name
        if not uid:
            self.uid = self._try_uid(0)
        elif 'i' in str(uid):
            self.uid = uid
        else:
            self.uid = f'i{uid}'

        self._group = None
        self.group = group

        self.defaults = [(time.time(), '')] if defaults in [None, []] else defaults
        self.note = '' if not note else note

        GroceryItem._uids.add(self.uid)  # Needed for uid calc

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return f'GroceryItem({self.name}, uid={self.uid}, {self.group.name}, ' \
               f'defaults={self.defaults}, note={self.note})'

    def __str__(self):
        return self.uid

    def _try_uid(self, n):
        _uid = 'i' + str(len(self._uids) + n).zfill(2)
        if _uid not in self._uids:
            return _uid
        else:
            return self._try_uid(n + 1)

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        if isinstance(value, DisplayGroup):
            self._group = value
        else:
            for _dict in [DisplayGroup._uids, DisplayGroup._names]:
                try:
                    self._group = _dict[value]
                except KeyError:
                    pass
                else:
                    break
            else:
                raise ValueError(self.group)
