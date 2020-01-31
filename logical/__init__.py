import os

from logical.stores import Store


for root, _, filenames in os.walk('data\\stores'):
    for store in filenames:
        name = store[:-4]
        s = Store(name, store)
        if name == 'default':
            Store.default = s


def as_string(tup):
    """Convert constant color tuples to lists for kivy.properties.ListProperties"""
    try:
        r, g, b, a = tup
    except ValueError:
        a = 1
        r, g, b = tup
    return f'{r}, {g}, {b}, {a}'


def as_list(tup):
    """Convert constant color tuples to lists for kivy.properties.ListProperties"""
    try:
        r, g, b, a = tup
    except ValueError:
        a = 1
        r, g, b = tup
    return [r, g, b, a]


def hide_widget(wid, dohide=True):
    if hasattr(wid, 'saved_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True
