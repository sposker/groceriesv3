from operator import itemgetter
from time import time

from kivy.clock import Clock
from kivy.graphics.context_instructions import Color
from kivy.properties import StringProperty, ObjectProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDFlatButton, BasePressedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.icon_definitions import md_icons

import logical
from logical.pools_and_lists import ItemPool
from widget_sections.preview import ItemCardContainer
from windows.dialogs import AddItemDialog


class SectionTitle(MDCard):
    """Widget holding group titles"""

    group = StringProperty()

    def __init__(self, grp, **kwargs):
        super().__init__(**kwargs)
        self.group = grp.name


class SectionAddItem(MDCard, ButtonBehavior):
    """Layout allowing item entry"""

    group = StringProperty()

    def __init__(self, grp, **kwargs):
        super().__init__(**kwargs)
        self.group = grp.name

    def on_release(self):
        AddItemDialog(self.group).open()


class ItemName(MDLabel):
    """Part of toggle button"""


class ItemCheckbox(MDIconButton):
    """Right side of toggle button"""

    icon = StringProperty()

    # @property
    # def text_color(self):
    #     if self.icon =


class ToggleLayout(MDCard):
    """ToggleButtons for items in db organized by group"""

    app = MDApp.get_running_app()

    group = None
    item = ObjectProperty()
    state = OptionProperty('normal', options=['normal', 'down'])
    icon = OptionProperty('checkbox-blank-outline', options=['checkbox-marked-outline', 'checkbox-blank-outline'])
    children_color = [logical.as_list(app.theme_cls.accent_color), app.text_color]

    def __init__(self, item, **kwargs):
        self.item = item
        super().__init__(**kwargs)
        self.color = self.app.text_color
        self.card = None
        self.state = 'normal'

    def toggle(self):
        """Defines toggle behavior for layout"""

        if self.state == 'normal':
            with ItemCardContainer() as f:
                self.card = f.add_card(toggle=self)
            self.state = 'down'
            graphics = [pair[0] for pair in [self.__class__.icon.options, self.children_color]]
        else:
            self.state = 'normal'
            with ItemCardContainer() as f:
                f.remove_card(self.card)
                self.card = None
            graphics = [pair[1] for pair in [self.__class__.icon.options, self.children_color]]

        self._graphics_toggle(graphics)

    def menu_delete(self):
        """Called when item deleted from ListPreview"""
        return self.toggle()

    def _graphics_toggle(self, graphics):
        for widget in self.children:
            try:
                _ = widget.icon
            except AttributeError:
                pass
            else:
                widget.icon = graphics[0]
            finally:
                widget.text_color = graphics[1]

    @staticmethod
    def _do_split(string):
        """`display_name` helper method"""
        _half, _ = half, x = divmod(len(string), 2)
        if string[half] == ' ':
            return string[:half] + '\n' + string[half+1:]
        while True:
            if x:
                half += 1
                if string[half] == ' ':
                    string = string[:half] + '\n' + string[half + 1:]
                    return string
            else:
                _half -= 1
                if string[_half] == ' ':
                    string = string[:_half] + '\n' + string[_half + 1:]
                    return string
            x = not x

    @property
    def display_name(self):
        """Split long names into readable, multiline text"""
        name = self.item.name
        if len(name) > 20:  # Split into two lines
            _name = self._do_split(name)
        else:
            _name = name
        return _name


class GroupScrollHelper(RelativeLayout):
    """Element background and scrollbar alignment"""
    pass


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

    cols = 3

    def __init__(self, grp, **kwargs):
        super().__init__(**kwargs)
        self._scrollview_pos = None
        self.widget_list = []
        self.group = grp
        self.generate()

    def generate(self):
        """Pull information from database to use when constructing subsection"""

        size_kwargs = {
            'size_hint': (1, None),
            'size': (self.width, self.app.item_row_height*9/8)
        }

        items = {item.name: item for item in self.app.db.items.values() if item.group == self.group}
        keys = sorted(list(items))
        keys.reverse()

        title = SectionTitle(self.group, **size_kwargs)
        add_button = SectionAddItem(self.group, **size_kwargs)

        if self.cols == 3:
            lab = Label(**size_kwargs)
            self.widget_list.append(lab)
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
        groups = [obj for obj in app.db.groups.values()]  # Values used for construction of display
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

            # self.add_widget(gridlayout)

        self.height = self.heightplaceholder

        def unpack(args):
            x = args[0], (args[1], 1 - args[2] / self.height, 1 - args[3] / self.height)
            return x

        self.heights = {k: v for k, v in (unpack(quad) for quad in self._heights_list)}

    def interpret_pool(self, pool: ItemPool):
        for uid, info in pool.items():
            try:
                item = self.app.db.items[uid]
            except KeyError:
                info = [info[0], (time(), info[1]), info[2]]
                kwargs = {k: v for k, v in zip(['name', 'defaults', 'note'], info)}
                item = self.app.db.add_new_item(kwargs)



