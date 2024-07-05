import io
import os
import sys
import math
import time
import click
import pygame
import random
import datetime
import requests
from account import WeatherAccount
from settings import Settings
from time import gmtime, strftime
from urllib.request import urlopen
#os.system('cls') #Windows
os.system('clear') #Linux

global unix, MapUnix, TopLeftArea
unix = int(time.time())
MapUnix = unix
settings = Settings()
account = WeatherAccount()
WeatherList = [0,0,0,0,'N/A']
CurrentSecond=0
ListCount=0
ListStart,ListEnd = 1,len([entry for entry in os.listdir(settings.dir_path) if os.path.isfile(os.path.join(settings.dir_path, entry))])

pygame.init()
if settings.screen_type == 'FULLSCREEN':
	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
	pygame.mouse.set_visible(False)
else:
	screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
pygame.display.set_caption("Analog Clock")
screen_w, screen_h = pygame.display.get_surface().get_size()

TopLeftArea = screen_h-(392/600*(screen_w*.5))

def _check_events():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.mouse.set_visible(True)
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				pygame.mouse.set_visible(True)
				sys.exit()

def CreateList():
	global BackgroundList, ListStart, ListEnd, ListCount
	ListCount=0
	ListStart,ListEnd = 1,len([entry for entry in os.listdir(settings.dir_path) if os.path.isfile(os.path.join(settings.dir_path, entry))])
	BackgroundList = []
	for file_path in os.listdir(settings.dir_path):
		if os.path.isfile(os.path.join(settings.dir_path, file_path)):
			BackgroundList.append(file_path)
	random.shuffle(BackgroundList)

def CreateBackground():
	try:
		screen.fill(settings.clock_bg_color)
		bg_image = pygame.image.load(f"{settings.dir_path}/{BackgroundList[ListCount]}")
		bg_orig_w, bg_orig_h = bg_image.get_size()
		if (bg_orig_w/screen_w >= bg_orig_h/screen_h):
			scaled_bg_image = pygame.transform.scale(bg_image, (int(bg_orig_w//(bg_orig_w/screen_w)), int(bg_orig_h//(bg_orig_w/screen_w))))
		else:
			scaled_bg_image = pygame.transform.scale(bg_image, (int(bg_orig_w//(bg_orig_h/screen_h)), int(bg_orig_h//(bg_orig_h/screen_h))))
		bg_rect = scaled_bg_image.get_rect()
		bg_rect.center = (screen_w/2, screen_h/2)
		screen.blit(scaled_bg_image, bg_rect)
		bg_text = BackgroundList[ListCount][:len(BackgroundList[ListCount])-4].split(' - ')
		screen.blit(font_size_4.render(f'{bg_text[0]}',True, settings.clock_face_color, settings.clock_bg_color), (20,20+font_size4*2))
		screen.blit(font_size_4.render(f'{bg_text[1]}',True, settings.clock_face_color, settings.clock_bg_color), (20,20+font_size4*1))
		screen.blit(font_size_4.render(f'{bg_text[2]}',True, settings.clock_face_color, settings.clock_bg_color), (20,20+font_size4*0))
		pygame.display.update()
	except FileNotFoundError:
		CreateList()

def UpdateBackground():
	global ListCount, BackgroundList
	if (int(time.strftime("%M")) in (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59)) & (int(time.strftime("%S")) == 0):
	#if (int(time.strftime("%S")) in (0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58)):
		CreateBackground()
		if (ListCount != (ListEnd-1)):
			ListCount += 1
		else:
			CreateList()
			ListCount=0

def ConvertDegreesToPyGame(R,theta):
	y = math.cos(2*math.pi*theta/360)*R
	x = math.sin(2*math.pi*theta/360)*R
	return x+ClockSizeW, -(y-ClockSizeH)

def MakeClock(h,m,s):
	global ClockSize, ClockSizeW, ClockSizeH
	CreateBackground()
	ClockSize=200
	ClockSizeW=int(ClockSize/2+20)
	ClockSizeH=int(screen_h-ClockSize/2-20)
	pygame.draw.circle(screen, settings.clock_face_color, (ClockSizeW,ClockSizeH), int(ClockSize/2-2))
	pygame.draw.circle(screen, settings.clock_font_color, (ClockSizeW,ClockSizeH), int(ClockSize/2), 3)

	#Face Ticks
	R1 = ClockSize*.49
	R2 = ClockSize*.49*.85
	theta = 0
	for _ in range(12):
		theta += 30
		pygame.draw.line(screen,(0,0,0), ConvertDegreesToPyGame(R1, theta), ConvertDegreesToPyGame(R2, theta), 3)

	#Hour Hand
	R = ClockSize*.5*.5
	theta = (h+m/60)*(360/12)
	pygame.draw.line(screen,(0,0,0), (ClockSizeW,ClockSizeH), ConvertDegreesToPyGame(R, theta), 7)

	#Minute Hand
	R = ClockSize*.5*.80
	theta = (m+s/60)*(360/60)
	pygame.draw.line(screen,(0,0,0), (ClockSizeW,ClockSizeH), ConvertDegreesToPyGame(R, theta), 4)

	#Second Hand
	R = ClockSize*.5*.85
	theta = s*(360/60)
	pygame.draw.aaline(screen,(255,0,0), (ClockSizeW,ClockSizeH), ConvertDegreesToPyGame(R, theta), 1)

def WeatherMapInt():
	global imageX
	imageX = {}
	imageX["image10"] = pygame.transform.scale(pygame.image.load(f"transparent.png"), (int(screen_w*.5),int(392/600*(screen_w*.5))))
	WeatherMap()

def WeatherMap():
	LOCALmap = 9
	for URLmap in range(0,10):
		try:
			#image_url = f"https://radar.weather.gov/ridge/standard/CONUS-LARGE_0.gif"
			image_url = f"https://radar.weather.gov/ridge/standard/CONUS_" + str(URLmap) + ".gif"
			image_str = urlopen(image_url, timeout=2).read()
			image_file = io.BytesIO(image_str)
			imageX["image{0}".format(LOCALmap)] = pygame.transform.scale(pygame.image.load(image_file), (int(screen_w*.5),int(392/600*(screen_w*.5))))
		except:
			imageX["image{0}".format(LOCALmap)] = imageX["image{0}".format(LOCALmap + 1)]
		LOCALmap -= 1

def WeatherMapBackground():
	num_str = repr(current_time[5])
	last_digit = int(num_str[-1])
	for MapDraw in range(0,10):
		if last_digit == MapDraw:
			screen.blit(imageX["image{0}".format(MapDraw)], (0,TopLeftArea))

def GetTwoFourHour():
	global WeatherList
	try:
		url = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat='+account.latitude+'&lon='+account.longitude+'&exclude=minutely,daily&units=imperial&lang=en&appid='+account.account, timeout=2)
		current_weather = url.json()
		WeatherList = [unix,current_weather['current']['dt'],int(round(current_weather['current']['temp'],1)),int(round(current_weather['current']['feels_like'],1)),current_weather['current']['weather'][0]['description'],current_weather['hourly'][0]['dt'],int(round(current_weather['hourly'][0]['temp'],1)),int(round(current_weather['hourly'][0]['feels_like'],1)),current_weather['hourly'][0]['weather'][0]['description'],current_weather['hourly'][1]['dt'],int(round(current_weather['hourly'][1]['temp'],1)),int(round(current_weather['hourly'][1]['feels_like'],1)),current_weather['hourly'][1]['weather'][0]['description'],current_weather['hourly'][2]['dt'],int(round(current_weather['hourly'][2]['temp'],1)),int(round(current_weather['hourly'][2]['feels_like'],1)),current_weather['hourly'][2]['weather'][0]['description'],current_weather['hourly'][3]['dt'],int(round(current_weather['hourly'][3]['temp'],1)),int(round(current_weather['hourly'][3]['feels_like'],1)),current_weather['hourly'][3]['weather'][0]['description'],current_weather['hourly'][4]['dt'],int(round(current_weather['hourly'][4]['temp'],1)),int(round(current_weather['hourly'][4]['feels_like'],1)),current_weather['hourly'][4]['weather'][0]['description'],current_weather['hourly'][5]['dt'],int(round(current_weather['hourly'][5]['temp'],1)),int(round(current_weather['hourly'][5]['feels_like'],1)),current_weather['hourly'][5]['weather'][0]['description'],current_weather['hourly'][6]['dt'],int(round(current_weather['hourly'][6]['temp'],1)),int(round(current_weather['hourly'][6]['feels_like'],1)),current_weather['hourly'][6]['weather'][0]['description'],current_weather['hourly'][7]['dt'],int(round(current_weather['hourly'][7]['temp'],1)),int(round(current_weather['hourly'][7]['feels_like'],1)),current_weather['hourly'][7]['weather'][0]['description'],current_weather['hourly'][8]['dt'],int(round(current_weather['hourly'][8]['temp'],1)),int(round(current_weather['hourly'][8]['feels_like'],1)),current_weather['hourly'][8]['weather'][0]['description'],current_weather['hourly'][9]['dt'],int(round(current_weather['hourly'][9]['temp'],1)),int(round(current_weather['hourly'][9]['feels_like'],1)),current_weather['hourly'][9]['weather'][0]['description'],current_weather['hourly'][10]['dt'],int(round(current_weather['hourly'][10]['temp'],1)),int(round(current_weather['hourly'][10]['feels_like'],1)),current_weather['hourly'][10]['weather'][0]['description'],current_weather['hourly'][11]['dt'],int(round(current_weather['hourly'][11]['temp'],1)),int(round(current_weather['hourly'][11]['feels_like'],1)),current_weather['hourly'][11]['weather'][0]['description'],current_weather['hourly'][12]['dt'],int(round(current_weather['hourly'][12]['temp'],1)),int(round(current_weather['hourly'][12]['feels_like'],1)),current_weather['hourly'][12]['weather'][0]['description'],current_weather['hourly'][13]['dt'],int(round(current_weather['hourly'][13]['temp'],1)),int(round(current_weather['hourly'][13]['feels_like'],1)),current_weather['hourly'][13]['weather'][0]['description'],current_weather['hourly'][14]['dt'],int(round(current_weather['hourly'][14]['temp'],1)),int(round(current_weather['hourly'][14]['feels_like'],1)),current_weather['hourly'][14]['weather'][0]['description'],current_weather['hourly'][15]['dt'],int(round(current_weather['hourly'][15]['temp'],1)),int(round(current_weather['hourly'][15]['feels_like'],1)),current_weather['hourly'][15]['weather'][0]['description'],current_weather['hourly'][16]['dt'],int(round(current_weather['hourly'][16]['temp'],1)),int(round(current_weather['hourly'][16]['feels_like'],1)),current_weather['hourly'][16]['weather'][0]['description'],current_weather['hourly'][17]['dt'],int(round(current_weather['hourly'][17]['temp'],1)),int(round(current_weather['hourly'][17]['feels_like'],1)),current_weather['hourly'][17]['weather'][0]['description'],current_weather['hourly'][18]['dt'],int(round(current_weather['hourly'][18]['temp'],1)),int(round(current_weather['hourly'][18]['feels_like'],1)),current_weather['hourly'][18]['weather'][0]['description'],current_weather['hourly'][19]['dt'],int(round(current_weather['hourly'][19]['temp'],1)),int(round(current_weather['hourly'][19]['feels_like'],1)),current_weather['hourly'][19]['weather'][0]['description'],current_weather['hourly'][20]['dt'],int(round(current_weather['hourly'][20]['temp'],1)),int(round(current_weather['hourly'][20]['feels_like'],1)),current_weather['hourly'][20]['weather'][0]['description'],current_weather['hourly'][21]['dt'],int(round(current_weather['hourly'][21]['temp'],1)),int(round(current_weather['hourly'][21]['feels_like'],1)),current_weather['hourly'][21]['weather'][0]['description'],current_weather['hourly'][22]['dt'],int(round(current_weather['hourly'][22]['temp'],1)),int(round(current_weather['hourly'][22]['feels_like'],1)),current_weather['hourly'][22]['weather'][0]['description'],current_weather['hourly'][23]['dt'],int(round(current_weather['hourly'][23]['temp'],1)),int(round(current_weather['hourly'][23]['feels_like'],1)),current_weather['hourly'][23]['weather'][0]['description'],current_weather['hourly'][24]['dt'],int(round(current_weather['hourly'][24]['temp'],1)),int(round(current_weather['hourly'][24]['feels_like'],1)),current_weather['hourly'][24]['weather'][0]['description']]
		os.environ[unix,current_weather['current']['dt'],int(round(current_weather['current']['temp'],1)),int(round(current_weather['current']['feels_like'],1)),current_weather['current']['weather'][0]['description'],current_weather['hourly'][0]['dt'],int(round(current_weather['hourly'][0]['temp'],1)),int(round(current_weather['hourly'][0]['feels_like'],1)),current_weather['hourly'][0]['weather'][0]['description'],current_weather['hourly'][1]['dt'],int(round(current_weather['hourly'][1]['temp'],1)),int(round(current_weather['hourly'][1]['feels_like'],1)),current_weather['hourly'][1]['weather'][0]['description'],current_weather['hourly'][2]['dt'],int(round(current_weather['hourly'][2]['temp'],1)),int(round(current_weather['hourly'][2]['feels_like'],1)),current_weather['hourly'][2]['weather'][0]['description'],current_weather['hourly'][3]['dt'],int(round(current_weather['hourly'][3]['temp'],1)),int(round(current_weather['hourly'][3]['feels_like'],1)),current_weather['hourly'][3]['weather'][0]['description'],current_weather['hourly'][4]['dt'],int(round(current_weather['hourly'][4]['temp'],1)),int(round(current_weather['hourly'][4]['feels_like'],1)),current_weather['hourly'][4]['weather'][0]['description'],current_weather['hourly'][5]['dt'],int(round(current_weather['hourly'][5]['temp'],1)),int(round(current_weather['hourly'][5]['feels_like'],1)),current_weather['hourly'][5]['weather'][0]['description'],current_weather['hourly'][6]['dt'],int(round(current_weather['hourly'][6]['temp'],1)),int(round(current_weather['hourly'][6]['feels_like'],1)),current_weather['hourly'][6]['weather'][0]['description'],current_weather['hourly'][7]['dt'],int(round(current_weather['hourly'][7]['temp'],1)),int(round(current_weather['hourly'][7]['feels_like'],1)),current_weather['hourly'][7]['weather'][0]['description'],current_weather['hourly'][8]['dt'],int(round(current_weather['hourly'][8]['temp'],1)),int(round(current_weather['hourly'][8]['feels_like'],1)),current_weather['hourly'][8]['weather'][0]['description'],current_weather['hourly'][9]['dt'],int(round(current_weather['hourly'][9]['temp'],1)),int(round(current_weather['hourly'][9]['feels_like'],1)),current_weather['hourly'][9]['weather'][0]['description'],current_weather['hourly'][10]['dt'],int(round(current_weather['hourly'][10]['temp'],1)),int(round(current_weather['hourly'][10]['feels_like'],1)),current_weather['hourly'][10]['weather'][0]['description'],current_weather['hourly'][11]['dt'],int(round(current_weather['hourly'][11]['temp'],1)),int(round(current_weather['hourly'][11]['feels_like'],1)),current_weather['hourly'][11]['weather'][0]['description'],current_weather['hourly'][12]['dt'],int(round(current_weather['hourly'][12]['temp'],1)),int(round(current_weather['hourly'][12]['feels_like'],1)),current_weather['hourly'][12]['weather'][0]['description'],current_weather['hourly'][13]['dt'],int(round(current_weather['hourly'][13]['temp'],1)),int(round(current_weather['hourly'][13]['feels_like'],1)),current_weather['hourly'][13]['weather'][0]['description'],current_weather['hourly'][14]['dt'],int(round(current_weather['hourly'][14]['temp'],1)),int(round(current_weather['hourly'][14]['feels_like'],1)),current_weather['hourly'][14]['weather'][0]['description'],current_weather['hourly'][15]['dt'],int(round(current_weather['hourly'][15]['temp'],1)),int(round(current_weather['hourly'][15]['feels_like'],1)),current_weather['hourly'][15]['weather'][0]['description'],current_weather['hourly'][16]['dt'],int(round(current_weather['hourly'][16]['temp'],1)),int(round(current_weather['hourly'][16]['feels_like'],1)),current_weather['hourly'][16]['weather'][0]['description'],current_weather['hourly'][17]['dt'],int(round(current_weather['hourly'][17]['temp'],1)),int(round(current_weather['hourly'][17]['feels_like'],1)),current_weather['hourly'][17]['weather'][0]['description'],current_weather['hourly'][18]['dt'],int(round(current_weather['hourly'][18]['temp'],1)),int(round(current_weather['hourly'][18]['feels_like'],1)),current_weather['hourly'][18]['weather'][0]['description'],current_weather['hourly'][19]['dt'],int(round(current_weather['hourly'][19]['temp'],1)),int(round(current_weather['hourly'][19]['feels_like'],1)),current_weather['hourly'][19]['weather'][0]['description'],current_weather['hourly'][20]['dt'],int(round(current_weather['hourly'][20]['temp'],1)),int(round(current_weather['hourly'][20]['feels_like'],1)),current_weather['hourly'][20]['weather'][0]['description'],current_weather['hourly'][21]['dt'],int(round(current_weather['hourly'][21]['temp'],1)),int(round(current_weather['hourly'][21]['feels_like'],1)),current_weather['hourly'][21]['weather'][0]['description'],current_weather['hourly'][22]['dt'],int(round(current_weather['hourly'][22]['temp'],1)),int(round(current_weather['hourly'][22]['feels_like'],1)),current_weather['hourly'][22]['weather'][0]['description'],current_weather['hourly'][23]['dt'],int(round(current_weather['hourly'][23]['temp'],1)),int(round(current_weather['hourly'][23]['feels_like'],1)),current_weather['hourly'][23]['weather'][0]['description'],current_weather['hourly'][24]['dt'],int(round(current_weather['hourly'][24]['temp'],1)),int(round(current_weather['hourly'][24]['feels_like'],1)),current_weather['hourly'][24]['weather'][0]['description']] = 'WeatherList'
		os.environ[unix] = 'WeatherList'
	except:
		WeatherList[0] = unix

def TwoFourHourOutlookDisp():
	screen.blit(font_size_3.render(f'Day&Time   Real/Feel   Sky Condition',True, settings.font_color), (screen_w*.525,screen_h/25*0)) # Display column header
	for WeatherOutlook in range(3,27):
		screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[((WeatherOutlook*4)-3)]).strftime("%a %#I:%M %p")} {WeatherList[((WeatherOutlook*4)-2)]}/{WeatherList[((WeatherOutlook*4)-1)]}\N{DEGREE SIGN}F {WeatherList[((WeatherOutlook*4)-0)].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*(WeatherOutlook-2)))

def ClockDisplay():
	if int(time.strftime("%I", current_time)) >= 10:
		screen.blit(font_size_1.render(TimeList[0],True, settings.font_color), (screen_w*.025,font_size1*.4)) # clock, single-digit hour
	else:
		screen.blit(font_size_1.render(f' {TimeList[0]}',True, settings.font_color), (screen_w*.025,font_size1*.4)) # clock, double-digit hour
	screen.blit(font_size_2.render(TimeList[1],True, settings.font_color), (font_size1*5.5,font_size1*.47)) # AM/PM
	screen.blit(font_size_3.render(f' {TimeList[2]}',True, settings.font_color), (font_size1*5.47,font_size1*1.06)) # CST/CDT
	screen.blit(font_size_2.render(f'{WeatherList[2]}\N{DEGREE SIGN}Real/{WeatherList[3]}\N{DEGREE SIGN}Feel',True, settings.font_color), (screen_w*.025,font_size1*1.6)) # Current Temp
	screen.blit(font_size_2.render(f'{WeatherList[4].title()}',True, settings.font_color), (screen_w*.025,font_size1*2.3)) # Current Sky Condition

def ClothingCheck():
	if min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck1: # Check for 'Coat Hat Gloves'
		screen.blit(font_size_2.render(f'{settings.TempAnswer1}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Coat Hat Gloves'
	elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck2: # Check for 'Coat'
		screen.blit(font_size_2.render(f'{settings.TempAnswer2}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Coat'
	elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck3: # Check for 'Long Sleeves'
		screen.blit(font_size_2.render(f'{settings.TempAnswer3}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Long Sleeves'
	elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck4: # Check for 'Short Sleeves'
		screen.blit(font_size_2.render(f'{settings.TempAnswer4}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Short Sleeves'

def WeekendCheck():
	global IsWeekend, IsWeekendState
	now = datetime.datetime.now()
	IsWeekend = now.strftime("%w")
	if (IsWeekend == '0') or (IsWeekend == '6'):
		IsWeekendState = 'true'
	else:
		IsWeekendState = 'false'

font_size1 = int(round(TopLeftArea/4,0))
font_size2 = int(round(font_size1/3*2,0))
font_size3 = int(round(screen_h/30,0))
font_size4 = int(round(screen_h/60,0))
font_size_1 = pygame.font.SysFont('dejavusansmono', font_size1)
font_size_2 = pygame.font.SysFont('dejavusansmono', font_size2)
font_size_3 = pygame.font.SysFont('dejavusansmono', font_size3)
font_size_4 = pygame.font.SysFont('dejavusansmono', font_size4)
if font_size3*2 >= 200:
	icon_use = '-4'
	icon_size = 200
elif font_size3*2 >= 100:
	icon_use = '-2'
	icon_size = 100
else:
	icon_use = ''
	icon_size = 50

CreateList()
while True:
	WeekendCheck()
	WeatherMapInt()
	while ((strftime("%R") >= settings.TimeRangeSrt1) & (strftime("%R") < settings.TimeRangeEnd1)) | ((strftime("%R") >= settings.TimeRangeSrt2) & (strftime("%R") < settings.TimeRangeEnd2) & (IsWeekendState != settings.IsWeekendTest)):
		if unix < int(time.time()):
			unix = int(time.time())
			_check_events()
			current_time = time.localtime()
			#TimeList = [time.strftime("%#I:%M:%S", current_time),time.strftime("%p", current_time),time.strftime("%Z", current_time)] #Windows
			TimeList = [time.strftime("%-I:%M:%S", current_time),time.strftime("%p", current_time),time.strftime("%Z", current_time)] #Linux
			if TimeList[2] == 'Central Daylight Time':
				TimeList[2] = 'CDT'
			else:
				TimeList[2] = 'CST'
			if MapUnix+settings.MapRefresh < unix:
				MapUnix = unix
				WeatherMap()
			if WeatherList[0]+settings.WeatherRefresh < unix:
				GetTwoFourHour()       
			screen.fill(settings.bg_color)
			WeatherMapBackground()
			ClockDisplay()
			ClothingCheck()
			TwoFourHourOutlookDisp()
			pygame.display.update()
	while ((strftime("%R") < settings.TimeRangeSrt1) | (strftime("%R") >= settings.TimeRangeEnd1)) & ((strftime("%R") < settings.TimeRangeSrt2) | (strftime("%R") >= settings.TimeRangeEnd2) | (IsWeekendState == settings.IsWeekendTest)):
		if int(time.strftime("%S")) != CurrentSecond:
			CurrentSecond = int(time.strftime("%S"))
			UpdateBackground()
			_check_events()
			h=int(time.strftime("%I"))
			m=int(time.strftime("%M"))
			s=int(time.strftime("%S"))
			MakeClock(h,m,s)
			pygame.display.update(pygame.Rect(20,screen_h-20-ClockSize,ClockSize,ClockSize))
