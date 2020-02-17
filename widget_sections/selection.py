from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from __init__ import as_list, TEXT_COLOR
from logical.state import ListState


class SectionHeader(BoxLayout):
    """Title for `DisplayGrid` containing add item function button"""

    def __init__(self, group, **kwargs):
        self.group = group
        super().__init__(**kwargs)


class PairedToggleButtons(MDRaisedButton):
    """ToggleButtons for items in db organized by group"""

    group = None
    item = ObjectProperty()
    icon = StringProperty()

    """
    Redeclaration of `width` property prevents excessive iteration, which seems to originate from implementation of
    `BaseRectangularButton` in kivymd.buttons-- but may in fact also be present somewhere else in the library.
    Either way, it's not worth adjusting that code or searching any further when this fix works.
    """
    width = NumericProperty()

    def __init__(self, item, **kwargs):
        self.item = item
        super().__init__(**kwargs)
        self.node = None
        self.text_color = TEXT_COLOR
        ListState.instance.toggles_dict[self.item.uid] = self

    def do_toggle(self):
        """When children are clicked"""

        if not self.node:
            self.node = ListState.instance.add_card(item=self.item, toggle=self)
        else:
            self.node = ListState.instance.remove_card(self.node)

    def graphics_toggle(self, state):
        if state == 'normal':
            self.icon = 'checkbox-blank-outline'
            self.text_color = self.app.text_color
        else:
            self.icon = 'checkbox-marked-outline'
            self.text_color = as_list(self.app.theme_cls.accent_color)

    @property
    def app(self):
        return MDApp.get_running_app()

    @property
    def display_name(self):
        """Split long names into readable, multiline text"""
        name = self.item.name
        if len(name) > 20:  # Split into two lines
            name = self._do_split(name)
        return name

    @staticmethod
    def _do_split(string):
        """`display_name` helper method"""
        half_, _ = half, x = divmod(len(string), 2)
        if string[half] == ' ':
            return string[:half] + '\n' + string[half + 1:]
        while True:
            if x:
                half += 1
                if string[half] == ' ':
                    string = string[:half] + '\n' + string[half + 1:]
                    return string
            else:
                half_ -= 1
                if string[half_] == ' ':
                    string = string[:half_] + '\n' + string[half_ + 1:]
                    return string
            x = not x


class GroupScrollHelper(RelativeLayout):
    """Element background and scrollbar alignment"""


class GroupScrollBar(ScrollView):
    """Scroll bar and methods for controlling bar"""

    instance = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GroupScrollBar.instance = self

    @property
    def heights(self):
        return GroupDisplay.instance.heights


class DisplayGrid(GridLayout):
    """Subsection of scrollview holding Groups"""

    def __init__(self, grp, items, **kwargs):
        super().__init__(**kwargs)
        self._scrollview_pos = None
        self.toggles_list = []
        self.group = grp
        self.generate(items)

    def generate(self, items):
        """Pull information from database to use when constructing subsection"""

        items_ = sorted(items, key=lambda i: i.name, reverse=True)

        while items_:
            toggle = self.toggle_cls(items_.pop())
            self.toggles_list.append(toggle)

    def populate(self):
        for widget in self.toggles_list:
            self.add_widget(widget)
        del self.toggles_list

    def set_position(self, top, bot):
        self._scrollview_pos = (top, bot)

    @property
    def sv_top(self):
        return 1 - self._scrollview_pos[0] / GroupDisplay.instance.height

    @property
    def sv_bot(self):
        return 1 - self._scrollview_pos[1] / GroupDisplay.instance.height

    @property
    def grid_rows(self):
        q, r = divmod(len(self.toggles_list) - 1, self.cols)
        return q

    @property
    def spacers_height(self):
        return (self.grid_rows - 1) * self.spacing[0]

    @property
    def toggle_cls(self):
        """Different toggle class for mobile and desktop"""
        return MDApp.get_running_app().toggle_cls


class GroupDisplay(BoxLayout):
    """Widget placed in scrollview; holds `SectionHeaders` and `DisplayGrids` (which hold toggle buttons)"""

    instance = None
    _heights_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GroupDisplay.instance = self

        self.app = MDApp.get_running_app()
        groups = self.app.db.items_by_group  # Values used for construction of display
        groups = sorted(groups.items(), key=lambda pair_: pair_[0].uid)
        self.heightplaceholder = 0

        for pair in groups:
            group, items = pair
            header = SectionHeader(group)
            gridlayout = DisplayGrid(group, items)

            top = self.heightplaceholder  # Top of grid section- pixels
            gridlayout.height = (gridlayout.grid_rows * self.app.item_row_height) \
                                  + gridlayout.spacers_height + self.header_height
            self.heightplaceholder += (self.header_height + gridlayout.height)  # Add height to running total
            gridlayout.set_position(top, self.heightplaceholder)

            self.add_widget(header)
            self.add_widget(gridlayout)
            gridlayout.populate()
            self._heights_list.append(
                (gridlayout.group.name, gridlayout, self.heightplaceholder - gridlayout.height, self.heightplaceholder))

        self.height = self.heightplaceholder

        def unpack(args):
            x = args[0], (args[1], 1 - args[2] / self.height, 1 - args[3] / self.height)
            return x

        self.heights = {k: v for k, v in (unpack(quad) for quad in self._heights_list)}

    @property
    def header_height(self):
        return self.app.item_row_height  # TODO: Fix for win/android
