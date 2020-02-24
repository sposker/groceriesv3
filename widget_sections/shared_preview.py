from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from logical.state import ListState


class ListScrollHelper(RelativeLayout):
    """Element background and scrollbar alignment"""
    pass


class ListScrollBar(ScrollView):
    """ScrollBar for list"""

    instance = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ListScrollBar.instance = self
        Clock.schedule_once(self._bar_width)

    def _bar_width(self, _):
        from widget_sections.selection import GroupScrollBar
        self.bar_width = GroupScrollBar.instance.bar_width


class ItemCardContainer(BoxLayout):
    """List preview displaying item cards"""

    instance = None
    sort_type = 'creation'

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        ItemCardContainer.instance = self

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def trigger_refresh(self):
        """Called when ListState is updated to signal a changed state"""
        self.height = ListState.instance.container_height


