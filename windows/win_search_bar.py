"""Unfortunately the kivyMD widget`MDTextFieldRound` makes it incredibly difficult to adjust methods of the child
widgets that contribute to the parent widget. Options are to waste resources building and then removing widgets,
or copy code to redefine an almost identical class, which will use subclasses of kivy widgets in place of the default
widgets. How difficult would it really have been to subclass these building blocks and allow the main widget to use
a view class for child widgets, allowing for substitution?
"""

from collections import defaultdict

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.widget import WidgetException
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from fuzzywuzzy import fuzz, process
from kivymd.uix.button import MDFlatButton


class PredictiveButton(MDFlatButton, FocusBehavior):
    """Button inside predictive text dropdown"""
    #
    #
    # def keyboard_on_key_down(self, window, keycode, text, modifiers):
    #     if keycode[0] == 273:
    #         self.get_focus_previous().focus = True
    #         return True
    #     elif keycode[1] == 274:
    #         self.get_focus_next().focus = True
    #         return True
    #     elif keycode == ...:
    #         ...
    #
    # def on_focus(self, *args):
    #     value = args[1]
    #     print(self, args)
    #     if value:
    #         self.text_color = MDApp.get_running_app().theme_cls.accent_color
    #         self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
    #         self._keyboard.bind(on_key_down=self._on_keyboard_down)
    #     else:
    #         self.text_color = MDApp.get_running_app().text_color
    #
    # def _keyboard_closed(self):
    #     print('My keyboard have been closed!')
    #     self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    #     self._keyboard = None
    #
    # def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    #     print('The key', keycode, 'have been pressed')
    #     print(' - text is %r' % text)
    #     print(' - modifiers are %r' % modifiers)
    #
    #     # Keycode is composed of an integer + a string
    #     # If we hit escape, release the keyboard
    #     if keycode[1] == 'escape':
    #         keyboard.release()
    #
    #     # Return True to accept the key. Otherwise, it will be used by
    #     # the system.
    #     return self.keyboard_on_key_down(keyboard, keycode, text, modifiers)
    #
    # def get_focus_next(self):
    #     return self.indices[self.index + 1]
    #
    # def get_focus_previous(self):
    #     return self.indices[self.index - 1]
    #
    # @property
    # def base_widget(self):
    #     return self.parent.attach_to.root.ids['field']


class PredictiveDropdown(DropDown):
    """Dropdown for possible item names"""

    def open(self, widget):
        if self.attach_to is not None:
            return
        super().open(widget)
        with self.attach_to.canvas:
            ...  # TODO


class SearchTextInput(TextInput):
    """Custom hotkey behavior"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = MDApp.get_running_app().db
        self.buttons = {}
        self._current_value = None
        self.btn_text_color = MDApp.get_running_app().text_color
        self.btn_active_color = MDApp.get_running_app().theme_cls.accent_color

    def keyboard_on_key_down(self, window, keycode, text, modifiers):

        if self.dropdown.attach_to:
            if keycode[0] == 273:
                return self.key_down_helper(-1)
            elif keycode[0] == 274:
                return self.key_down_helper(1)
        super().keyboard_on_key_down(window, keycode, text, modifiers)

    def key_down_helper(self, value):
        try:
            self.current_value += value
        except TypeError:
            self.current_value = 2 if value == -1 else 0
            self.root.icon_left_color = self.btn_text_color
        color_icon = True
        for index, widget in self.buttons.items():
            if index == self.current_value:
                widget.text_color = self.btn_active_color
                color_icon = False
            else:
                widget.text_color = self.btn_text_color
        if color_icon:
            self.root.icon_left_color = self.btn_active_color
        return True

    def on_text(self, *_):
        if not len(self.text) > 1:
            self.dropdown.dismiss()
            return
        options = process.extractBests(self.text,
                                       self.db.item_names,
                                       scorer=(fuzz.token_sort_ratio if ' ' not in self.text
                                               else fuzz.token_set_ratio),
                                       # score_cutoff=min(40 + len(self.text)**2, 90),
                                       limit=3)
        self.dropdown.clear_widgets()
        self.current_value = None
        for index, pair in enumerate(options):
            w = PredictiveButton(text=pair[0])
            self.dropdown.add_widget(w)
            self.buttons[index] = w
        try:
            self.dropdown.open(self.root)
        except WidgetException:
            print('widget_exception')

    @property
    def dropdown(self):
        return self.root.dropdown

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        if value not in range(3):
            self._current_value = None
        else:
            self._current_value = value


class WinSearchBar(ThemableBehavior, BoxLayout):
    __events__ = ("on_text_validate", "on_focus")

    # font related properties from TextInput
    font_context = StringProperty()
    font_family = StringProperty()
    font_name = StringProperty("Roboto")
    font_size = NumericProperty(15)

    active_color = ListProperty([1, 1, 1, 0.2])
    allow_copy = BooleanProperty(True)
    event_focus = ObjectProperty()  # Called at the moment of focus/unfocus of the text field.
    focus = BooleanProperty()
    icon_left = StringProperty("magnify")
    icon_left_color = ListProperty([1, 1, 1, 1])
    icon_left_disabled = BooleanProperty(True)
    normal_color = ListProperty([1, 1, 1, 0.5])
    radius = NumericProperty(dp(25))  # The values ​​of the rounding of the corners of the text field.
    text = StringProperty()
    text_validate_unfocus = BooleanProperty(True)  # Whether on_text_validate() should unfocus the field
    write_tab = BooleanProperty(False)

    _current_color = ListProperty()
    _outline_color = ListProperty([0, 0, 0, 0])
    _instance_icon_left = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_color = self.normal_color
        self.dropdown = PredictiveDropdown()

    def _on_focus(self, field):
        self._current_color = (
            self.active_color if field.focus else self.normal_color
        )
        self.get_color_line(field, field.text, field.focus)
        if self.event_focus:
            self.event_focus(self, field, field.focus)
        self.focus = field.focus
        self.dispatch("on_focus")
        self._instance_icon_left.text_color = (
            self.theme_cls.accent_color
            if field.focus
            else self.icon_left_color
        )
        if field.focus:
            field.select_text(0, len(field.text))

    def on_normal_color(self, _instance, value):
        self._current_color = value

    def get_color_line(self, _field_instance, _field_text, field_focus):
        if not field_focus:
            self._outline_color = [0, 0, 0, 0]
        else:
            self._outline_color = self.theme_cls.primary_color

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode in (273, 274):
            print('consumed')
            return True
        super().keyboard_on_key_down(window, keycode, text, modifiers)

    def on_text_validate(self):
        try:
            text = self.field.buttons[self.field.current_value].text
        except KeyError:
            text = self.field.text
        self.icon_left_color = MDApp.get_running_app().text_color
        return self.fire_text(text)

    def on_focus(self, *_):
        pass

    def fire_text(self, text):
        print(text)

    # def on_focus(self, *args):
    #     if args and args[1] is False:
    #         Clock.schedule_once(lambda _: setattr(self.global_focus, 'focus', True))
