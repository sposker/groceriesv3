import time

from logical import UIDRoot


class DisplayGroup(UIDRoot):
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


class GroceryItem(UIDRoot):
    _uids = set()

    def __init__(self,
                 name=None,
                 group=None,
                 defaults=None,
                 note=None,
                 uid=None,
                 ):

        if not name:
            raise ValueError('Item name cannot be `None`')

        self.name = name

        if not uid:
            self.uid = self._try_uid(0)
        elif 'i' in str(uid):
            self.uid = uid
        else:
            self.uid = f'i{uid}'

        self._group = None  # Set by @group.setter
        self.group = group  # ibid
        self.defaults = self.set_defaults(defaults)
        self.note = '' if not note else note

        GroceryItem._uids.add(self.uid)  # Needed for uid calc

    def __str__(self):
        return f'{self.name} ({self.uid})'

    def __repr__(self):
        return (
            f'{self.__class__}('
            f'{self.name},'
            f'uid={self.uid},'
            f'group={self.group.name},'
            f'defaults={self.defaults},'
            f'note={self.note}'
            f')'
        )

    def _try_uid(self, n):
        uid_ = 'i' + str(len(self._uids) + n).zfill(3)
        if uid_ not in self._uids:
            return uid_
        else:
            return self._try_uid(n + 1)

    @staticmethod
    def set_defaults(old):
        if not old:
            return [(int(round(time.time())), '\u00B7')]  # u00B7 is a unicode dot

        defaults = []
        for time_, value_ in old:
            try:
                value = int(value_)
            except (TypeError, ValueError):
                value = '\u00B7'
            defaults.append((int(time_), value))
        return defaults

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        if isinstance(value, DisplayGroup):
            self._group = value
        else:
            for dict_ in [DisplayGroup._uids, DisplayGroup._names]:
                try:
                    self._group = dict_[value]
                except KeyError:
                    pass
                else:
                    break
            else:
                raise ValueError(self.group)
