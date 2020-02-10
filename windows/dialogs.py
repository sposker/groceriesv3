import os
import smtplib
import ssl
from datetime import datetime
from operator import itemgetter

from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField

from logical.pools_and_lists import ShoppingList, ItemPool


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
            i = self.values.pop(self.values.index(AddItemDialog.group))
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
        from widget_sections.preview import ItemCardContainer

        info = {k: v for k, v in [('name', self.field.text), ('group', self.spinner.text)]}

        self.dismiss()
        with ItemCardContainer() as f:
            f.dialog_add_card(info)


class ClearListDialog(GroceriesAppBaseDialog):

    @staticmethod
    def clear_list():
        from widget_sections.preview import ItemCardContainer
        with ItemCardContainer() as f:
            children = f.children.copy()
            for card in children:
                f.remove_card(card)


class CompleteDialog(GroceriesAppBaseDialog):
    """Shown when list is completed"""

    def __init__(self, message, gro_list, **kwargs):
        self.message = message
        self.gro_list = gro_list
        super().__init__(**kwargs)

    def do_exit(self):
        app = MDApp.get_running_app()
        app.exit_routine(gro_list=self.gro_list)


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

        for widget in self.walk(restrict=True):
            if isinstance(widget, GridLayout):
                grid = widget  # there are actually two gridlayouts but we want the second one here
            elif isinstance(widget, MDTextField):
                field = widget
                field.root = self

        Clock.schedule_once(lambda _: setattr(field, 'focus', True))

        for i in range(2, -1, -1):
            for j in range(1, 4):
                # noinspection PyUnboundLocalVariable
                grid.add_widget(DefaultsDialogButton(3 * i + j, self))

    def write_input(self, value):
        """Set main button text to given value"""
        self.main_button.text = f'{value}'
        self.dismiss()


class ExitDialog(GroceriesAppBaseDialog):
    """When corner X is clicked"""

    def do_save(self):
        from widget_sections.preview import ItemCardContainer
        with ItemCardContainer() as f:
            gro_list = f.convert_to_pool()
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
        y, m, d, _, _ = filename.split('.')
        self.display_name = f'{m}-{d}'
        self.path = os.path.join(root, filename)
        self.popup = popup
        super().__init__(**kwargs)
        self.__class__.instances += 1

    def on_release(self):
        from widget_sections.selection import GroupDisplay
        self.popup.clear_list()
        pool = ItemPool.from_file(self.path)
        GroupDisplay.instance.interpret_pool(pool)
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
        self.app = MDApp.get_running_app()
        self.db = self.app.db
        self.gro_list = None

    def make_list(self, store_name='default'):
        store = self.db.stores[store_name]
        path = x if (x := self.app.lists_path) else 'data\\username\\lists'
        self.gro_list = ShoppingList(self.item_pool, store, path)

    @staticmethod
    def send_email(content):
        """Read login info from credentials and access server to send email"""
        with open('data\\credentials.txt') as f:
            sender_email, receiver_email, password = [line.split(':')[1][:-1] for line in f]
            print(f'{sender_email}::{receiver_email}::{password}')

        port = 465  # For SSL
        context = ssl.create_default_context()  # Create a secure SSL context
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, content)

    def print_list(self):
        self.make_list()
        self.gro_list.format_plaintext()
        self.gro_list.write(doprint=True)

        self.complete('List saved;\nPrinting in progress')

    def email_list(self):
        self.make_list()
        self.gro_list.format_plaintext()
        self.gro_list.write()
        self.send_email(self.gro_list.email_content)

        self.complete('List sent via Email')

    def save_formatted_list(self):
        self.item_pool.dump_yaml()
        print('dumped')
        # print(self.gro_list)
        self.make_list()
        # print(self.gro_list)
        self.gro_list.format_plaintext()
        # print(self.gro_list)
        self.gro_list.write()
        # print(self.gro_list)

        self.complete('List saved')

    def save_incomplete(self):
        self.item_pool.dump_yaml()

        self.complete('Items saved to disk.')

    def complete(self, text):
        self.dismiss()
        Factory.CompleteDialog(text, self.item_pool).open()


class SettingsDialog(GroceriesAppBaseDialog):

    @staticmethod
    def do_exit():
        ...
