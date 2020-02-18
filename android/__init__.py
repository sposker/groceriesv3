from kivy.core.window import Window
from kivy.factory import Factory

from widget_sections.dialogs import DefaultsDialog, FilePickerDialog
# Actually need to import this somewhere to have it registered for .kv files
# noinspection PyUnresolvedReferences
from widget_sections.search import ListFunctionsBar, MyMDIconButton

ITEM_ROW_HEIGHT = 240
TEXT_BASE_SIZE = 40

Window.size = (1080, 1920)
Window.borderless = True

Factory.register('DefaultsDialog', cls=DefaultsDialog)
Factory.register('FilePickerDialog', cls=FilePickerDialog)

