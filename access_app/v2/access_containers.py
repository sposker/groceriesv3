#
# from abc import ABC, abstractmethod
#
# from kivy.uix.boxlayout import BoxLayout
# from kivymd.app import MDApp
#
# from access_app.access_misc_widgets import AccessRecycleView
# # from access_app.view_classes import GroupDetailRow, ItemDetailRow, LocationMapRow, LocationDetailRow
# from access_app.access_view_registers import DataFactory
#
#
#
# class ContainerFactory:
#
#     def __init__(self, **kwargs):
#         self._creators = kwargs
#
#     def register(self, name, container):
#         self._creators[name] = container
#
#     def get(self, format_, *args):
#         container_cls, view_cls = self._creators[format_]
#         container_cls.layout = view_cls
#         return container_cls(*args)
