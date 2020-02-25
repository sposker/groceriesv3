from kivymd.app import MDApp

from logical.groups_and_items import DisplayGroup


class GroupDetailLogic:
    """"""

    def shift_up(self):
        ...

class ItemDetailLogic:
    """"""

    def _gather_info(self):
        """Update item properties based on entered values"""
        self.item.name = self.widget_refs['item_name'].text
        self.item.group = self._convert_group()
        self.item.defaults = self._convert_defaults()
        self.item.note = self.widget_refs['item_note'].text

    def update_value(self, gather=True):
        """Save the current row of values"""

        if gather:
            self._gather_info()

        for index, nested in enumerate(self.rv.data):
            if nested['item_uid'] == self.item_uid:
                break

        new_value = ItemDetail(self.item).kv_pairs
        self.rv.data[index] = new_value
        self.rv.refresh_from_data()

    def reset_values(self):
        """Simply refresh the data without updating it, restoring previous values."""
        return self.update_value(gather=False)

    def _convert_defaults(self) -> list:
        """Build a new list of defaults based on input"""
        defaults = self.item.defaults
        while len(defaults) < 3:
            defaults.append(None)
        new_values = [self.widget_refs['defaults' + str(n)].text for n in range(2)]

        new_defaults = []
        for pair, val in zip(self.item.defaults, new_values):
            if val == '':
                continue
            try:
                t, num = pair
            except TypeError:
                import time
                t, num = int(round(time.time())), pair
            new_defaults.append((t, val))
        return new_defaults

    def _convert_group(self) -> DisplayGroup:
        """Find a new group object based on input"""
        text = self.widget_refs['group_name'].text
        if text == self.item.group.name:
            return self.item.group
        else:
            if not self.db:
                ItemDetailsLayout.db = MDApp.get_running_app().db
            for group in self.db.groups.values():
                if group.name == text:
                    return group

    @property
    def data_copy(self):
        if self._old_data is None:
            self._old_data = ItemDetail(self.item).kv_pairs
        return self._old_data

    @data_copy.deleter
    def data_copy(self):
        self._old_data = None

    @property
    def widget_refs(self) -> dict:
        """Create dict when needed rather than by default"""
        if self._widget_refs is None:
            self._widget_refs = {}
            for w in self.children:
                try:
                    n = getattr(w, 'widget_name')
                except AttributeError:
                    pass
                else:
                    self._widget_refs[n] = w
        return self._widget_refs

    @classmethod
    def update_all(cls):
        new_data = []


class LocationMapLogic:
    """"""


class LocationDetailLogic:
    """"""

