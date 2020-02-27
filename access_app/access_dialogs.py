from kivymd.app import MDApp

from widget_sections.dialogs import GroceriesAppBaseDialog


class MappingAttemptedNewItem(GroceriesAppBaseDialog):
    """Message explaining that new mappings can't be directly created."""

    def __init__(self, item_pool, **kwargs):
        super().__init__(**kwargs)
        self.item_pool = item_pool
        self.app = MDApp.get_running_app()

    def list_instructions(self, *args):
        """Wrap some calls with administrative tasks related to saving"""
        # self.item_pool.dump_yaml()
        io = self.app.io_manager
        for callable_ in args:
            list_method = getattr(io, callable_)
            result = list_method(self.item_pool)
        self.dismiss()
        # noinspection PyUnboundLocalVariable
        Factory.CompleteDialog(result, self.item_pool).open()