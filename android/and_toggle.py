from functools import partial
from threading import Event

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, ObjectProperty

from widget_sections.selection import PairedToggleButtons


class LongPressToggle(PairedToggleButtons):
    """Add long press functionality for Android"""

    __events__ = ('on_long_press',)
    long_press_time = Factory.NumericProperty(1)
    group = None
    item = ObjectProperty()
    icon = StringProperty()

    mutex = Event()

    def __init__(self, item, **kwargs):
        super().__init__(item, **kwargs)

        self._clockev = None

        self.bind(
            on_touch_down=self.create_clock,
            on_touch_up=self.delete_clock)

    def create_clock(self, widget, touch, *args):
        if not self.mutex.is_set():
            self.mutex.set()
            callback = partial(self.on_long_press, touch)
            self._clockev = Clock.schedule_once(callback, 1)
            touch.ud['on_long_press'] = callback

    def delete_clock(self, widget, touch, *args):
        try:
            self._clockev.cancel()
        except AttributeError:
            pass
        finally:
            self._clockev = None
            self.mutex.clear()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        pass  # TODO

        # if not self.node:
        #     print(self.item)
        #     self.node = ListState.instance.add_card(item=self.item, toggle=self)
        #     self.node.card.show_details()





