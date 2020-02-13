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

from __init__ import as_list
from logical.state import ListState
from widget_sections.dialogs import AddItemDialog


class SectionTitle(MDCard):
    """Widget holding group titles"""

    group = StringProperty()

    def __init__(self, group, **kwargs):
        super().__init__(**kwargs)
        self.group = group.name


class SectionAddItem(MDCard, ButtonBehavior):
    """Layout allowing item entry"""

    group = StringProperty()

    def __init__(self, group, **kwargs):
        super().__init__(**kwargs)
        self.group = group.name

    def on_release(self):
        AddItemDialog(self.group).open()


class ItemName(MDLabel):
    """Part of toggle button"""


class ItemCheckbox(MDIconButton):
    """Right side of toggle button"""

    icon = StringProperty()


class ToggleLayout(MDRaisedButton):
    """ToggleButtons for items in db organized by group"""

    width = NumericProperty()
    """
    Redeclaration of `width` property prevents excessive iteration, which seems to originate from implementation of
    `BaseRectangularButton` in kivymd.buttons but may in fact also be present somewhere else in the library.
    """

    group = None
    item = ObjectProperty()
    icon = StringProperty()
    app = MDApp.get_running_app()

    def __init__(self, item, **kwargs):
        self.item = item
        super().__init__(**kwargs)
        self.node = None
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
            return string[:half] + '\n' + string[half+1:]
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


class DisplaySubsection(GridLayout):
    """Subsection of scrollview holding Groups"""

    def __init__(self, grp, **kwargs):
        super().__init__(**kwargs)
        self._scrollview_pos = None
        self.widget_list = []
        self.group = grp
        self.generate()

    def generate(self):
        """Pull information from database to use when constructing subsection"""

        size_kwargs = {'size_hint': (1, None), 'size': (self.width, self.app.item_row_height * 9 / 8)}

        items = {item.name: item for item in self.app.db.items.values() if item.group == self.group}
        keys = sorted(list(items), reverse=True)

        title = SectionTitle(self.group, **size_kwargs)
        add_button = SectionAddItem(self.group, **size_kwargs)

        if self.cols == 3:
            extra_spacer = Widget(**size_kwargs)
            self.widget_list.append(extra_spacer)
        self.widget_list.append(title)
        self.widget_list.append(add_button)

        while keys:
            name = keys.pop()
            item = items[name]
            toggle = ToggleLayout(item)
            self.widget_list.append(toggle)

    def populate(self):
        for widget in self.widget_list:
            self.add_widget(widget)
        del self.widget_list

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
        q, r = divmod(len(self.widget_list) - 1, 3)
        return q + 1


class GroupDisplay(BoxLayout):
    """Widget placed in scrollview; holds DisplaySubsections (which hold toggle buttons)"""

    instance = None
    _heights_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        GroupDisplay.instance = self

        self.app = MDApp.get_running_app()
        groups = [obj for obj in self.app.db.groups.values()]  # Values used for construction of display
        groups.reverse()
        self.heightplaceholder = 0

        while groups:
            group = groups.pop()
            gridlayout = DisplaySubsection(group)

            top = self.heightplaceholder  # Top of grid section- pixels
            gridlayout.height = (gridlayout.grid_rows + 9 / 8) * self.app.item_row_height
            self.heightplaceholder += gridlayout.height  # Add height to running total
            gridlayout.set_position(top, self.heightplaceholder)

            self.add_widget(gridlayout)
            gridlayout.populate()
            self._heights_list.append(
                (gridlayout.group.name, gridlayout, self.heightplaceholder-gridlayout.height, self.heightplaceholder))

        self.height = self.heightplaceholder

        def unpack(args):
            x = args[0], (args[1], 1 - args[2] / self.height, 1 - args[3] / self.height)
            return x

        self.heights = {k: v for k, v in (unpack(quad) for quad in self._heights_list)}

