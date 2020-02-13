from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.managerswiper import MDSwiperManager


class LoadScreen(Screen):

    def do_load(*_):
        return MDApp.get_running_app().load_data()

    def on_enter(self, *args):
        Clock.schedule_once(self.do_load, 2)


class SelectionScreen(Screen):
    """Pick items to add to preview"""


class PreviewScreen(Screen):
    """Shows list in progress"""


class DetailsScreen(Screen):
    """Shows item details"""


class SearchScreen(Screen):
    """"""


class MobileManager(MDSwiperManager):
    """Manages various screens"""

    # def swith_screen(self, direction):
    #     print(direction)
    #     if direction == "right":
    #         if self.index_screen == 0:
    #             pass
    #         else:
    #             self.index_screen -= 1
    #     else:
    #         if self.index_screen == len(self.screen_names) - 1:
    #             pass
    #         else:
    #             self.index_screen += 1
    #
    #     print(self.index_screen)
    #
    #     self.transition.direction = direction
    #     if self.current != (scrn := self.screen_names[self.index_screen]):
    #         self.current = scrn
    #     if self.paginator:
    #         self.paginator.set_current_screen_round(self.index_screen)
    #
    #     # self.on_complete()

    def swith_screen(self, direction):
        print('direction')
        if direction == "right":
            if self.index_screen == 0:
                self.index_screen = len(self.screen_names) - 1
            else:
                self.index_screen -= 1
        else:
            self.index_screen += 1
        if self.index_screen >= len(self.screen_names) and direction != "right":
            self.index_screen = 0
        self.transition.direction = direction
        self.current = self.screen_names[self.index_screen]
        if self.paginator:
            self.paginator.set_current_screen_round(self.index_screen)
