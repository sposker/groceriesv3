from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDRectangleFlatIconButton


class MySpinnerButton(MDFlatButton):
    pass


class AccessSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = MDApp.get_running_app().db
        self.values = [grp.name for grp in self.db.groups.values()]


class ViewSortButton(MDRectangleFlatButton):
    """Buttons for sorting"""

    def sort(self):
        # print(self.rv_base.content.children[0])
        rv = self.rv_base.content.children[0]
        data = sorted(rv.data, key=lambda x: x[self.sort_key])
        if self.sort_dir == 'ascending':
            self.sort_dir = 'descending'
        else:
            self.sort_dir = 'ascending'
            data.reverse()
        rv.data = data
        rv.refresh_from_data()


class RecycleViewContainer(RecycleBoxLayout):
    """Container holding sub-layouts."""


class AccessRecycleView(RecycleView):
    """Holds various layouts in different sections of app."""

    def __init__(self, data_dict, viewclass=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data_dict
        self.viewclass = viewclass


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