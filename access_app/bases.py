from abc import ABC, abstractmethod

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel


class AccessBaseRow(BoxLayout):
    """Shared visual properties across various layout classes (defined in kv)"""


class DataGenerator(AccessBaseRow):
    """Layout for viewing relevant item information"""

    def __init__(self, element, **kwargs):
        self.element = element
        super().__init__(**kwargs)

    @property
    def kv_pairs(self):
        raise NotImplementedError

    @property
    def sort_key(self):
        # print(self)
        return self.element.uid


class DataFactory:

    def __init__(self, **kwargs):
        self._creators = kwargs

    def register(self, name, data_cls):
        self._creators[name] = data_cls

    def get(self, format_, elements: iter):
        view_cls = self._creators[format_]
        if format_ in ('group_details', 'location_details'):
            yield from (view_cls(e) for e in elements)
        else:
            yield from (view_cls(args).kv_pairs for args in elements)


class LayoutContainer(ABC):
    """Containers holding various representations of elements"""

    layout = None

    def __init__(self):
        self.data = []
        self.container_display = None

    @abstractmethod
    def generate_data(self, elements):
        raise NotImplementedError

    @abstractmethod
    def to_layout(self):
        raise NotImplementedError


class ContainerFactory:

    def __init__(self, **kwargs):
        self._creators = kwargs

    def register(self, name, container):
        self._creators[name] = container

    def get(self, format_, *args):
        container_cls, view_cls = self._creators[format_]
        return container_cls(*args)


class AccessTabbedPanel(TabbedPanel):
    """Tabbed panels root"""

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        for name, section in self.ids.items():
            if name == 'default_tab_id':
                continue
            section.populate()
