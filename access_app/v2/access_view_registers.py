# from kivy.uix.boxlayout import BoxLayout
#
# from access_app.v2.access_view_methods import GroupDetailLogic, LocationDetailLogic, LocationMapLogic, ItemDetailLogic
#
#
# class AccessBaseRow(BoxLayout):
#     """Shared properties across various layout classes"""
#
#
# class DataGenerator:
#     """Layout for viewing relevant item information"""
#
#     def __init__(self, *args, **kwargs):
#         self.element = args[0]
#         super().__init__(**kwargs)
#
#     def generate_data(self, container_format):
#         container_format.data.append(self.kv_pairs)
#
#     @property
#     def kv_pairs(self):
#         raise NotImplementedError
#
#     @property
#     def sort_key(self):
#         return self.element.uid
#
#
#
#
# class DataFactory:
#
#     def __init__(self, **kwargs):
#         self._creators = kwargs
#
#     def register(self, name, container):
#         self._creators[name] = container
#
#     def get(self, format_, *args):
#         view_cls = self._creators[format_]
#         view = view_cls()
#
#         if args:
#             setattr(view, 'store', args[0])
#         return view
