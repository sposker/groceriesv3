from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.widget import Widget


def populate_mod_group(db, producer, child_cls):
    """Create root widget for modifying `DisplayGroup` information"""

    group_details = producer.refreshed_group_details(db)
    container = BoxLayout(orientation='vertical',
                          spacing=8,
                          )

    for nested in sorted(group_details, key=lambda x: x['group_uid']):
        widget = child_cls(nested)
        container.add_widget(widget)

    return container


def populate_item_details(db, producer, parent_cls, child_cls):
    """Create `AccessRecycleView` for editing item details"""

    item_details = producer.refreshed_item_details(db)
    container = parent_cls(item_details, viewclass=child_cls)
    child_cls.rv = container
    return container


def populate_location_mapping(db, producer, base, view_cls):
    """Mapping for locations to items"""

    pairs = producer.refreshed_store_mappings(db)
    dict_ = {}
    values = []
    for mapping, store in pairs:
        dict_[store.name] = mapping
        values.append(store.name)
    base = base()
    base.values = values
    rv = RecycleView(viewclass=view_cls)
    rv.data = mapping
    base.add_widget(rv)
    rv.refresh_from_data()
    base.options = values

    return base


def populate_location_details(db, producer, sub_tab_panel, child_cls):
    """Editing location names and ordering"""

    pairs = producer.refreshed_location_details(db)

    sub = sub_tab_panel(do_default_tab=False,
                        tab_width=Window.width/len(pairs),
                        )
    for mapping, store in pairs:
        print(len(mapping))
        header = TabbedPanelHeader(text=store.name)
        content_ = BoxLayout(orientation='vertical')
        header.content = content_
        content_.add_widget(Widget(size_hint=(1, .08)))
        sub.add_widget(header)
        bx = BoxLayout(orientation='vertical', size_hint=(1, .92))
        content_.add_widget(bx)
        for dict_ in sorted(mapping, key=lambda x: x['location_uid']):
            widget = child_cls(dict_)
            bx.add_widget(widget)
        header.rv_ref = bx

    return sub
