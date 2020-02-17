import os

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import NumericProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton

from logical.pools_and_lists import ListWriter
from logical.state import ListState
from widget_sections.dialogs import FilePickerButton


TOOLBAR_ICON = None


def walk_toolbar(disabled=True):
    """Walk widgets"""
    if TOOLBAR_ICON:
        widget = TOOLBAR_ICON
    else:
        toolbar = MDApp.get_running_app().toolbar
        for widget in toolbar.walk(restrict=True):
            try:
                if widget.icon in ('arrow-right-bold-outline', 'arrow-left-bold-outline'):
                    break
            except AttributeError:
                pass
        else:
            return
    widget.disabled = disabled
    return widget


class DialogButton(MDRectangleFlatIconButton):

    def on_kv_post(self, base_widget):
        icon = self.ids['lbl_ic']
        icon.font_size = MDApp.get_running_app().text_base_size * 1.2


class LoadScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self._trigger = Clock.create_trigger(self.real_load, 2)

    def on_enter(self, *_):
        self._trigger()

    def real_load(self, *_):
        """Displays load screen while app builds itself"""
        self.app.load_data()
        return Clock.schedule_once(self.swap_screen)

    def swap_screen(self, *_):
        """Once loading is complete, swap the screen"""
        return setattr(self.app.manager, 'current', "picker")


class SelectionScreen(Screen):
    """Pick items to add to preview"""

    def on_enter(self, *args):
        """Update toolbar"""
        widget = walk_toolbar(disabled=False)
        widget.icon = 'arrow-right-bold-outline'
        setattr(widget, 'on_release', lambda: setattr(self.parent, 'current', 'preview'))
        self.parent.transition.direction = 'left'


class PreviewScreen(Screen):
    """Shows list in progress"""

    def on_enter(self, *args):
        """Update toolbar"""
        widget = walk_toolbar(disabled=False)
        widget.icon = 'arrow-left-bold-outline'
        setattr(widget, 'on_release', lambda: setattr(self.parent, 'current', 'picker'))
        self.parent.transition.direction = 'right'


class DetailsScreen(Screen):
    """Shows item details"""

    instance = None

    def __init__(self, card,  **kw):
        self.card = card
        super().__init__(**kw)

    def on_enter(self, *args):
        self.parent.transition.direction = 'right'
        walk_toolbar()

    def do_save(self):
        note = self.ids['note_input']
        self.card.note_display.text = note.text  # TODO node state
        for btn in self.ids['amount'].children:
            if btn.state == 'down':
                self.card.amount.text = btn.text
                break
        self.parent.current = 'preview'

    def do_leave(self):
        self.parent.current = 'preview'

    def on_leave(self, *args):
        manager = MDApp.get_running_app().manager
        manager.remove_widget(self)

    def add_defaults(self, defaults):
        from android.and_card import FloatingButton

        amount = self.ids['amount']
        widgets = [FloatingButton(v) for v in defaults] + [FloatingButton('+')]

        for w in widgets:
            amount.add_widget(w)
            if w.text == self.card.amount.text:
                w.text_color = MDApp.get_running_app().theme_cls.accent_color
                w.state = 'down'


class SearchScreen(Screen):
    """"""


class ListLoaderScreen(Screen):
    """Load lists over the network"""

    def on_enter(self, *args):
        walk = os.walk(MDApp.get_running_app().pools_path)
        root, _, filenames = next(walk)

        sorted_names = sorted(filenames, reverse=True)

        if self.ids['grid_container'].children:
            return

        for filename in sorted_names:
            if FilePickerButton.instances >= self.options:
                break
            btn = FilePickerButton(self, root, filename)
            self.ids['grid_container'].add_widget(btn)

    @staticmethod
    def clear_list():
        ListState.instance.clear()
        ListState.instance.container.clear_widgets()

    @staticmethod
    def dismiss():
        """Called when trying to dismiss popup"""
        MDApp.get_running_app().manager.current = 'preview'


class SaveScreen(Screen):
    """"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.item_pool = self.writer = None
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        walk_toolbar()
        self.item_pool = ListState.instance.convert_to_pool()

    def print_list(self):
        ...

    def email_list(self):
        ...

    def save_incomplete(self):
        ...

    def dismiss(self):
        self.app.manager.current = 'preview'

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





