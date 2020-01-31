import ctypes

user32 = ctypes.windll.user32
screenwidth, screenheight = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
# screenwidth, screenheight = 1920, 1080
