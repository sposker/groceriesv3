import os
import smtplib
import ssl
from datetime import datetime
from operator import itemgetter
from time import time

from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField

from logical.stores import ShoppingList


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

    # noinspection PyUnboundLocalVariable
    def do_add(self, *_):
        from widget_sections.preview import ItemCardContainer
        """Called when adding a new item"""
        for widget in self.walk(restrict=True):
            if isinstance(widget, self.AddItemSpinner):
                _group = widget.groups[widget.text]
            if isinstance(widget, MDTextField):
                _name = widget.text

        self.dismiss()
        with ItemCardContainer() as f:
            f.add_card(None, time())


class ClearListDialog(GroceriesAppBaseDialog):
    pass


class CompleteDialog(GroceriesAppBaseDialog):
    """Shown when list is completed"""
    # message = ''

    # def __init__(self, message, gro_list, **kwargs):
    #     self.message = message
    #     self.gro_list = gro_list
    #     super().__init__(**kwargs)
    #
    # def do_exit(self):
    #     app = App.get_running_app()
    #     app.exit_routine(gro_list=self.gro_list)


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
            gro_list = f.construct_grocery_list()
        Factory.SaveDialog(gro_list, MDApp.get_running_app().db).open()
        self.dismiss()

    @staticmethod
    def do_exit():
        MDApp.get_running_app().exit_routine()


class FilePickerDialog(GroceriesAppBaseDialog):
    """Load Files"""

    # def __init__(self, **kwargs):
    #     self.filepicker_path = os.getcwd() + '\\lists'
    #     super().__init__(**kwargs)
    #
    # def load(self, path, filename):
    #     try:
    #         with open(os.path.join(path, filename[0])) as stream:
    #             app = App.get_running_app()
    #             app.load_list(''.join([line for line in stream]))
    #             self.dismiss()
    #     except IndexError:
    #         pass


class SaveDialog(GroceriesAppBaseDialog):
    """Save the list"""

    def __init__(self, gro_list, db, **kwargs):
        super().__init__(**kwargs)
        self.gro_list = gro_list
        self.db = db



    @staticmethod
    def send_email(content):
        """Read login info from credentials and access server to send email"""
        with open('data\\credentials.txt') as f:
            fields = [line.split(':')[1] for line in f]

        sender_email, receiver_email, password = fields
        port = 465  # For SSL
        # Create a secure SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("len.r.wilkinson@gmail.com", password)
            server.sendmail(sender_email, receiver_email, content)



    def print_list(self):
        self.gro_list.format_plaintext()
        self.gro_list.write()
        self.print_physical()

        self.complete('List saved; Printing in progress')

    def email_list(self):
        self.gro_list.format_plaintext()
        self.gro_list.write()
        self.send_email(self.gro_list.format_email())

        self.complete('List sent via Email')

    def save_list(self):
        self.gro_list.format_plaintext()
        self.gro_list.write()

        self.complete('List saved')

    def complete(self, text):
        self.dismiss()
        Factory.CompleteDialog(text, self.gro_list).open()


class SettingsDialog(GroceriesAppBaseDialog):

    @staticmethod
    def do_exit():
        ...
