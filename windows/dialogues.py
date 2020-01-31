from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp

from kivy.factory import Factory
from kivy.uix.popup import Popup


from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton


class AddItemDialog(Popup):
    """Dialog for adding new item"""
    # class AddItemSpinner(Spinner):
    #
    #     def __init__(self, **kwargs):
    #         app = App.get_running_app()
    #         self.groups = {group.name: group for group in app.db.groups.values()}
    #         self.values = [n for n in self.groups.keys()]
    #         i = self.values.pop(self.values.index(AddItemDialog.group.name))
    #         self.values.insert(0, i)
    #
    #         super().__init__(**kwargs)
    #
    # def __init__(self, group, **kwargs):
    #     AddItemDialog.group = group
    #     super().__init__(**kwargs)
    #
    # def do_add(self, *_):
    #     """This is necessary to allow defining these widgets in .kv file"""
    #     for grid in self.children:
    #         for popup in grid.children:
    #             for rel in popup.children:
    #                 for widget in rel.children:
    #                     if isinstance(widget, self.AddItemSpinner):
    #                         _group = widget.groups[widget.text]
    #                     if isinstance(widget, TextInput):
    #                         _name = widget.text
    #     self.dismiss()
    #     ListPreview.instance.add_item(_name, time(), is_new=_group)


class ClearListDialog(Popup):
    pass


class CompleteDialog(Popup):
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


class ExitDialog(Popup):
    """When corner X is clicked"""

    def do_save(self):
        # gro_list = ListPreview.instance.build_list()
        self.dismiss()
        # Factory.SavePopup(gro_list, self.app.db).open()

    @staticmethod
    def do_exit():
        MDApp.get_running_app().exit_routine()

class FilePickerDialog(Popup):
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


class SaveDialog(Popup):
    """Save the list"""

    # def __init__(self, gro_list, db, **kwargs):
    #     super().__init__(**kwargs)
    #     self.gro_list = gro_list
    #     self.db = db
    #
    # @staticmethod
    # def save_to_text(text, do_print=False):
    #     date = str(datetime.datetime.now()).split(" ")[0]
    #     y, m, d = date.split('-')
    #     date = f'{y}.{m}.{d}.'
    #     filename = date + 'ShoppingList'
    #     path = os.getcwd()
    #     abspath = f'{path}\\lists\\{filename}.txt'
    #
    #     with open(abspath, 'w') as f:
    #         f.write(text)
    #
    #     if do_print:
    #         os.startfile(abspath, 'print')
    #
    # @staticmethod
    # def send_email(content):
    #     sender_email = "len.r.wilkinson@gmail.com"
    #     receiver_email = "oliver.wilkinson.1@gmail.com"
    #     message = content
    #     port = 465  # For SSL
    #     password = "Rockwell0368"
    #     # Create a secure SSL context
    #     context = ssl.create_default_context()
    #     with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    #         server.login("len.r.wilkinson@gmail.com", password)
    #         server.sendmail(sender_email, receiver_email, message)
    #
    # def format_list(self, shopping: ShoppingList, email=False):
    #     subject = f" ShoppingList {shopping.header['date']}"
    #     header = f"{shopping.header['date']}: Grocery List\n"
    #     if len(shopping.header) != 1:
    #         subject += ': '
    #
    #         _uns = 'l00'  # Keys for special locations
    #         _wal = 'l01'
    #         _del = 'l03'
    #
    #         if shopping.header[_uns]:
    #             header += f"List contains {shopping.items[_uns]} unsorted item(s).\n"
    #             subject += f"UNS:{shopping.header['unsorted']}- "
    #         if shopping.header[_wal]:
    #             header += f"List includes {len(shopping.items[_wal])} Wal-mart items.\n"
    #             subject += 'WAL-'
    #         if shopping.header[_del]:
    #             header += "List contains Deli items-- deli closes at 8pm.\n"
    #             subject += 'DELI'
    #     body = ''
    #     s = sorted([(k, v) for k, v in shopping.items.items()], key=itemgetter(0))
    #     for uid, nested in s:
    #         loc = self.db.locations[uid]
    #         body += f'\n{loc.name.capitalize()}:\n'
    #         for item, pair in nested.items():
    #             loc = item.name
    #             num, note = pair
    #             item_line = f'  {loc}'
    #             if num:
    #                 item_line += f': {num}'
    #             if note:
    #                 item_line += f'\n    -{note}'
    #             item_line += '\n'
    #             body += item_line
    #     if email:
    #         return f'Subject: {subject}\n\n{header}{body}'
    #     else:
    #         return f'{header}{body}'
    #
    # def print_list(self):
    #     body = self.format_list(self.gro_list)
    #     self.save_to_text(body, do_print=True)
    #     self.complete('List saved; Printing in progress')
    #
    # def email_list(self):
    #     body = self.format_list(self.gro_list)
    #     self.save_to_text(body)
    #
    #     body = self.format_list(self.gro_list, email=True)
    #     self.send_email(body)
    #
    #     self.complete('List sent via Email')
    #
    # def save_list(self):
    #     body = self.format_list(self.gro_list)
    #     self.save_to_text(body)
    #     self.complete('List saved')
    #
    # def complete(self, text):
    #     self.dismiss()
    #     Factory.CompleteDialog(text, self.gro_list).open()


class SettingsDialog(Popup):

    @staticmethod
    def do_exit():
        ...
