import os
from functools import wraps

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import NumericProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField

from logical.pools_and_lists import ListWriter, ItemPool
from logical.state import ListState


class GroceriesAppBaseDialog(Popup):
    """Canvas, colors, etc for popups"""


class AddItemDialog(GroceriesAppBaseDialog):
    """Dialog for adding new item"""
    group = None

    class AddItemSpinner(Spinner):

        def __init__(self, **kwargs):
            app = MDApp.get_running_app()
            self.groups = {group.name: group for group in app.db.groups.values()}
            self.values = [n for n in self.groups.keys()]
            i = self.values.pop(self.values.index(AddItemDialog.group.name))
            self.values.insert(0, i)

            super().__init__(**kwargs)

    def __init__(self, group, **kwargs):
        AddItemDialog.group = group
        super().__init__(**kwargs)

        for widget in self.walk(restrict=True):
            if isinstance(widget, self.AddItemSpinner):
                self.spinner = widget
            if isinstance(widget, MDTextField):
                self.field = widget

        Clock.schedule_once(lambda _: setattr(self.field, 'focus', True))

    def do_add(self, *_):
        """Called when adding a new item"""

        info = {k: v for k, v in [('name', self.field.text), ('group', self.spinner.text)]}
        item = MDApp.get_running_app().db.add_new_item(info)
        self.dismiss()
        ListState.instance.add_card(item=item)


class ClearListDialog(GroceriesAppBaseDialog):

    @staticmethod
    def clear_list():
        ListState.instance.clear()
        ListState.instance.container.clear_widgets()


class CompleteDialog(GroceriesAppBaseDialog):
    """Shown when list is completed"""

    def __init__(self, message, gro_list, pool, **kwargs):
        self.message = message
        self.gro_list = gro_list
        self.pool = pool
        super().__init__(**kwargs)

    def do_exit(self):
        app = MDApp.get_running_app()
        app.exit_routine(gro_list=self.gro_list, pool=self.pool)


class DefaultsDialogButton(MDIconButton):
    def __init__(self, value, root, **kwargs):
        super().__init__(**kwargs)
        self.icon = f'numeric-{value}-circle-outline'
        self.root = root
        self.value = value

    def on_release(self):
        self.root.write_input(self.value)


class DefaultsInput(MDTextField):

    def on_text_validate(self):
        self.root.write_input(self.text)


class DefaultsDialog(GroceriesAppBaseDialog):

    def __init__(self, main_button, **kwargs):
        super().__init__(**kwargs)
        self.main_button = main_button
        self.root_ = main_button.root

        field = None

        for widget in self.walk(restrict=True):
            if isinstance(widget, GridLayout):
                grid = widget  # there are actually two gridlayouts but we want the second one here
            elif isinstance(widget, MDTextField):
                field = widget
                field.root = self

        if field:
            Clock.schedule_once(lambda _: setattr(field, 'focus', True))

        for i in range(2, -1, -1):
            for j in range(1, 4):
                # noinspection PyUnboundLocalVariable
                grid.add_widget(DefaultsDialogButton(3 * i + j, self))

    def write_input(self, value):
        """Set main button text to given value"""
        self.main_button.text = f'{value}'
        self.root_.node.amount = value
        self.dismiss()


class ExitDialog(GroceriesAppBaseDialog):
    """When corner X is clicked"""

    def do_save(self):
        gro_list = ListState.instance.convert_to_pool()
        Factory.SaveDialog(gro_list).open()
        self.dismiss()

    @staticmethod
    def do_exit():
        MDApp.get_running_app().exit_routine()


class FilePickerButton(MDFlatButton, ToggleButtonBehavior):
    """Button for picking files"""

    instances = 0

    def __init__(self, popup, root, filename, **kwargs):
        self.filename = filename
        y, m, d, _filename, _ext = filename.split('.')
        self.display_name = f'{m}-{d}'
        self.path = os.path.join(root, filename)
        self.popup = popup
        super().__init__(**kwargs)
        self.__class__.instances += 1

    def on_release(self):
        self.popup.clear_list()
        pool = ItemPool.from_file(self.path)
        ListState.instance.populate_from_pool(pool)
        self.popup.dismiss()


class FilePickerDialog(GroceriesAppBaseDialog):
    """The builtin file picker is too obfuscated/ poorly documented to customize, so we'll just not use it"""

    options = NumericProperty()  # Number of visible widgets

    def __init__(self, **kwargs):
        self.app = MDApp.get_running_app()
        self.filepicker_path = x if (x := self.app.pools_path) else \
            os.path.join(os.getcwd(), r'data\username\lists')
        super().__init__(**kwargs)
        self.display_options()

    def display_options(self):
        """Load the list of choices"""
        walk = os.walk(self.filepicker_path)
        root, _, filenames = next(walk)

        sorted_names = sorted(filenames)
        sorted_names.reverse()

        for filename in sorted_names:
            if FilePickerButton.instances >= self.options:
                break
            btn = FilePickerButton(self, root, filename)
            self.ids['grid_container'].add_widget(btn)

    @staticmethod
    def clear_list():
        return ClearListDialog.clear_list()


class SaveDialog(GroceriesAppBaseDialog):
    """Show options for saving ItemPool to disk, with or without formatting"""

    def __init__(self, item_pool, **kwargs):
        super().__init__(**kwargs)
        self.item_pool = item_pool
        self.writer = None
        self.app = MDApp.get_running_app()

    def make_list(self, store_name='default'):
        """Map a store to items"""
        store = self.app.db.stores[store_name]
        path = path_ if (path_ := self.app.lists_path) else 'data\\username\\lists'
        self.writer = ListWriter(self.item_pool, store, path)

    def list_instructions(self, *args):
        """Wrap some calls with administrative tasks related to saving"""
        self.item_pool.dump_yaml()
        self.make_list()
        for callable_ in args:
            list_method = getattr(self.writer, callable_)
            result = list_method()
        self.dismiss()
        # noinspection PyUnboundLocalVariable
        Factory.CompleteDialog(result, self.writer, self.item_pool).open()


class SettingsDialog(GroceriesAppBaseDialog):

    @staticmethod
    def do_exit():
        ...
