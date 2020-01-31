#! python3


import kivy.utils

if kivy.utils.platform == 'win':
    from windows.win_app import WinApp as GroApp

if kivy.utils.platform == 'android':
    from android.and_app import MobileApp as GroApp

if __name__ == '__main__':
    GroApp().run()

