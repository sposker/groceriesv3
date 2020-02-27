from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDRectangleFlatIconButton


class MySpinnerButton(MDFlatButton):
    pass


class AccessSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = MDApp.get_running_app().db


class ViewSortButton(MDRectangleFlatButton):
    """Buttons for sorting"""

    def __init__(self, **kwargs):
        self._rv_instance = None
        self.sort_desc = False
        super().__init__(**kwargs)

    def sort(self):
        data = sorted(self.rv.data, key=lambda x: x[self.sort_key], reverse=self.sort_desc)
        self.sort_desc = not self.sort_desc
        self.rv.data = data
        self.rv.refresh_from_data()

    @property
    def rv(self):
        if self._rv_instance is None:
            try:
                self._direct_rv()
            except AttributeError:
                self._nested_rv()
        return self._rv_instance

    def _direct_rv(self):
        for child in self.container.children:
            if isinstance(child, AccessRecycleView):
                self._rv_instance = child

    def _nested_rv(self):
        self._rv_instance = self.container.container_display


class RecycleViewContainer(RecycleBoxLayout):
    """Container holding sub-layouts."""


class AccessRecycleView(RecycleView):
    """Holds various layouts in different sections of app."""

    def __init__(self, data_dict, viewclass=None, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = viewclass
        self.data = data_dict


class AccessMidButton(MDRectangleFlatIconButton):
    """Button that is visible on all tabbed panel screens"""

    mapping = {
        # 'Group Names & Order': None,
        # 'Item Details': None,
        # 'Item: Location Mapping': None,
        # 'Location Names & Order': None
    }

    def add_new_entry(self, tab):
        return self.mapping[tab.text]

    def update_from_view(self, tab):
        ...

    def dump_data(self, tab):
        ...

    @staticmethod
    def stop_app():
        return MDApp.get_running_app().stop()
