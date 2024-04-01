import pygame
pygame.font.init()

class Settings:
	#Weather Settings
	MapRefresh = 300
	WeatherRefresh = 900
	bg_color = (0,0,0)
	font_color = (255,255,255)

	#Full Screen Mode
	screen_type = 'FULLSCREEN'

	#only used for windowed mode
	#screen_type = 'WINDOWED' #Un-comment this line for windowed mode
	screen_width = 1680
	screen_height = 1050

	#Weather Check Settings
	TempCheck1 = 34
	TempCheck2 = 40
	TempCheck3 = 46
	TempCheck4 = 60
	TempAnswer1 = 'COAT HAT GLOVES'
	TempAnswer2 = 'COAT'
	TempAnswer3 = 'LONG SLEEVES'
	TempAnswer4 = 'SHORT SLEEVES'

	#Clock Settings
	clock_bg_color =  (31,31,31)
	clock_face_color =  (255,160,0)
	clock_font_color =  (0,0,0)

	#Clock/Weather time switching setting
	TimeRangeSrt1 = "06:30"
	TimeRangeEnd1 = "08:30"
	TimeRangeSrt2 = "14:30"
	TimeRangeEnd2 = "15:30"
	IsWeekendTest = 'true'

	#Image Path (relative to running location)
	dir_path = r'Images'
