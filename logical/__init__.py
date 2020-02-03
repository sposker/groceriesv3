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
            wid.height, wid.size_hint[1], wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint[1], wid.opacity, wid.disabled
        wid.height, wid.size_hint[1], wid.opacity, wid.disabled = 0, None, 0, True
