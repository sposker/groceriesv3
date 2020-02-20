#! python3.8


import kivy.utils

if kivy.utils.platform == 'android':
    from android.android_app import MobileApp as GroApp
else:
    from windows.win_app import WinApp as GroApp

if __name__ == '__main__':
    GroApp().run()

