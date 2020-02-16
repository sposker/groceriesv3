from kivy.clock import Clock
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


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
        toolbar = MDApp.get_running_app().toolbar
        for widget in toolbar.walk(restrict=True):
            try:
                if widget.icon in ('arrow-right-bold-outline', 'arrow-left-bold-outline'):
                    break
            except AttributeError:
                pass
        else:
            return
        widget.icon = 'arrow-right-bold-outline'
        setattr(widget, 'on_release', lambda: setattr(self.parent, 'current', 'preview'))
        self.parent.transition.direction = 'left'


class PreviewScreen(Screen):
    """Shows list in progress"""

    def on_enter(self, *args):
        """Update toolbar"""
        toolbar = MDApp.get_running_app().toolbar
        for widget in toolbar.walk(restrict=True):
            try:
                if widget.icon in ('arrow-right-bold-outline', 'arrow-left-bold-outline'):
                    break
            except AttributeError:
                pass
        else:
            return
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
        btns = ToggleButtonBehavior.get_widgets('defaults_toggles')
        print(btns)
        del btns

        amount = self.ids['amount']
        for c in amount.children:
            try:
                print(c.group)
            except AttributeError:
                c.group = 'defaults_toggles'

    def add_defaults(self, defaults):
        from android.and_card import FloatingButton

        amount = self.ids['amount']
        widgets = [FloatingButton(v) for v in defaults]

        for w in widgets:
            amount.add_widget(w)
        widgets[0].state = 'down'


class SearchScreen(Screen):
    """"""


