"""Unfortunately the kivyMD widget`MDTextFieldRound` makes it incredibly difficult to adjust methods of the child
widgets that contribute to the parent widget. Options are to waste resources building and then removing widgets,
or copy code to redefine an almost identical class, which will use subclasses of kivy widgets in place of the default
widgets. How difficult would it really have been to subclass these building blocks and allow the main widget to use
a view class for child widgets, allowing for substitution?
"""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivymd.theming import ThemableBehavior


class SearchTextInput(TextInput):
    """Custom hotkey behavior"""


class WinSearchBar(ThemableBehavior, BoxLayout):

    __events__ = ("on_text_validate", "on_text", "on_focus")

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

    def on_text_validate(self):
        pass

    def on_text(self, *args):
        pass

    def on_focus(self, *args):
        if args and args[1] is False:
            Clock.schedule_once(lambda _: setattr(self.global_focus, 'focus', True))

