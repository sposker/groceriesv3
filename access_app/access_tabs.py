from abc import ABC, abstractmethod

from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivymd.app import MDApp


class AccessBaseLayout(ABC, BoxLayout):
    """Shared properties across various layout classes"""

    @abstractmethod
    def populate(self):
        raise NotImplementedError


class ModGroupTab(AccessBaseLayout):
    """Allows adjusting display group names and order"""

    group_name = StringProperty()
    group_uid = StringProperty()

    def populate(self):
        app = MDApp.get_running_app()
        container = app.container_factory.get('mod_groups')
        for group in app.db.groups.values():
            view = app.view_factory.get('mod_groups', group)
            view.generate_data()  # Appends data from object to container's data
        container.to_layout()
        self.content.add_widget(container.display)


class ItemDetailsTab(AccessBaseLayout):
    """For editing item details, no mappings."""

    item = ObjectProperty()
    item_uid = StringProperty()
    item_name = StringProperty()
    item_group_uid = StringProperty()
    item_group_name = StringProperty()
    item_default_0 = StringProperty()
    item_default_1 = StringProperty()
    item_default_2 = StringProperty()
    item_note = StringProperty()

    def populate(self):
        app = MDApp.get_running_app()
        container = app.container_factory.get('item_details')
        for item in app.db.items.values():
            view = app.view_factory.get('item_details', item)
            view.generate_data()  # Appends data from object to container's data
        container.to_layout()
        self.content.add_widget(container.display)


class ItemLocationTab(AccessBaseLayout):
    """Entry for mapping location to item"""

    item_name = StringProperty()
    item_uid = StringProperty()
    location_name = StringProperty()
    location_uid = StringProperty()

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.content.children[0]
        for store in app.db.stores.values():
            store_panel = TabbedPanelItem()
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('map_locations', store)
            for item in store.locations.items:
                view = app.view_factory.get('map_locations', item)
                view.generate_data()  # Appends data from object to container's data
            container.to_layout()
            store_panel.content = container.display


class ModLocationsTab(AccessBaseLayout):
    """Allows adjusting Location names and order"""

    location_name = StringProperty()
    location_uid = StringProperty()

    pairs = {}

    def populate(self):
        app = MDApp.get_running_app()
        sub_panel = self.content.children[0]
        for store in app.db.stores.values():
            store_panel = TabbedPanelItem()
            sub_panel.add_widget(store_panel)
            container = app.container_factory.get('mod_locations', store)
            for location in store.locations.values():
                view = app.view_factory.get('mod_locations', location)
                view.generate_data()  # Appends data from object to container's data
            container.to_layout()
            store_panel.content = container.display


class AccessTabbedPanel(TabbedPanel):
    """Tabbed panels root"""

    mapping = {
        'mod_groups': ModGroupTab,
        'item_details': ItemDetailsTab,
        'locs_map': ItemLocationTab,
        'mod_locs': ModLocationsTab,
    }

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        for name, section in self.ids.items():
            base_layout = self.mapping[name]
            section.content = base_layout()
            section.content.populate()
