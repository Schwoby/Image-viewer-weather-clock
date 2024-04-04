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
	global BackgroundList, ListStart, ListEnd
	ListStart,ListEnd = 1,len([entry for entry in os.listdir(settings.dir_path) if os.path.isfile(os.path.join(settings.dir_path, entry))])
	BackgroundList = []
	for file_path in os.listdir(settings.dir_path):
		if os.path.isfile(os.path.join(settings.dir_path, file_path)):
			BackgroundList.append(file_path)
	random.shuffle(BackgroundList)

def CreateBackground():
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

def UpdateBackground():
	global ListCount, BackgroundList
	if (int(time.strftime("%M")) in (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59)) & (int(time.strftime("%S")) == 0):
	#if (int(time.strftime("%S")) in (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59)):
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

def WeatherMap():
	global image0, image1, image2, image3, image4, image5, image6, image7, image8, image9
	try:
		#image_url = f"https://radar.weather.gov/ridge/standard/CONUS-LARGE_0.gif"
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_0.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image9 = pygame.image.load(image_file)
	except:
		image9 = pygame.image.load(f"transparent.png")
	image9 = pygame.transform.scale(image9, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_1.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image8 = pygame.image.load(image_file)
	except:
		image8 = image9
	image8 = pygame.transform.scale(image8, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_2.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image7 = pygame.image.load(image_file)
	except:
		image7 = image8
	image7 = pygame.transform.scale(image7, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_3.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image6 = pygame.image.load(image_file)
	except:
		image6 = image7
	image6 = pygame.transform.scale(image6, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_4.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image5 = pygame.image.load(image_file)
	except:
		image5 = image6
	image5 = pygame.transform.scale(image5, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_5.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image4 = pygame.image.load(image_file)
	except:
		image4 = image5
	image4 = pygame.transform.scale(image4, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_6.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image3 = pygame.image.load(image_file)
	except:
		image3 = image4
	image3 = pygame.transform.scale(image3, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_7.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image2 = pygame.image.load(image_file)
	except:
		image2 = image3
	image2 = pygame.transform.scale(image2, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_8.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image1 = pygame.image.load(image_file)
	except:
		image1 = image2
	image1 = pygame.transform.scale(image1, (int(screen_w*.5),int(392/600*(screen_w*.5))))
	try:
		image_url = f"https://radar.weather.gov/ridge/standard/CONUS_9.gif"
		image_str = urlopen(image_url).read()
		image_file = io.BytesIO(image_str)
		image0 = pygame.image.load(image_file)
	except:
		image0 = image1
	image0 = pygame.transform.scale(image0, (int(screen_w*.5),int(392/600*(screen_w*.5))))

def WeatherMapBackground():
	if last_digit == 0:
		screen.blit(image0, (0,TopLeftArea))
	elif last_digit == 1:
		screen.blit(image1, (0,TopLeftArea))
	elif last_digit == 2:
		screen.blit(image2, (0,TopLeftArea))
	elif last_digit == 3:
		screen.blit(image3, (0,TopLeftArea))
	elif last_digit == 4:
		screen.blit(image4, (0,TopLeftArea))
	elif last_digit == 5:
		screen.blit(image5, (0,TopLeftArea))
	elif last_digit == 6:
		screen.blit(image6, (0,TopLeftArea))
	elif last_digit == 7:
		screen.blit(image7, (0,TopLeftArea))
	elif last_digit == 8:
		screen.blit(image8, (0,TopLeftArea))
	else:
		screen.blit(image9, (0,TopLeftArea))

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
	WeatherMap()
	while ((strftime("%R") >= settings.TimeRangeSrt1) & (strftime("%R") < settings.TimeRangeEnd1)) | ((strftime("%R") >= settings.TimeRangeSrt2) & (strftime("%R") < settings.TimeRangeEnd2) & (IsWeekendState != settings.IsWeekendTest)):
		if unix < int(time.time()):
			unix = int(time.time())
			_check_events()
			current_time = time.localtime()
			num_str = repr(current_time[5])
			last_digit = int(num_str[-1])
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
				try:
					url = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat='+account.latitude+'&lon='+account.longitude+'&exclude=minutely,daily&units=imperial&lang=en&appid='+account.account)
					current_weather = url.json()
					WeatherList = [unix,current_weather['current']['dt'],int(round(current_weather['current']['temp'],1)),int(round(current_weather['current']['feels_like'],1)),current_weather['current']['weather'][0]['description'],current_weather['hourly'][0]['dt'],int(round(current_weather['hourly'][0]['temp'],1)),int(round(current_weather['hourly'][0]['feels_like'],1)),current_weather['hourly'][0]['weather'][0]['description'],current_weather['hourly'][1]['dt'],int(round(current_weather['hourly'][1]['temp'],1)),int(round(current_weather['hourly'][1]['feels_like'],1)),current_weather['hourly'][1]['weather'][0]['description'],current_weather['hourly'][2]['dt'],int(round(current_weather['hourly'][2]['temp'],1)),int(round(current_weather['hourly'][2]['feels_like'],1)),current_weather['hourly'][2]['weather'][0]['description'],current_weather['hourly'][3]['dt'],int(round(current_weather['hourly'][3]['temp'],1)),int(round(current_weather['hourly'][3]['feels_like'],1)),current_weather['hourly'][3]['weather'][0]['description'],current_weather['hourly'][4]['dt'],int(round(current_weather['hourly'][4]['temp'],1)),int(round(current_weather['hourly'][4]['feels_like'],1)),current_weather['hourly'][4]['weather'][0]['description'],current_weather['hourly'][5]['dt'],int(round(current_weather['hourly'][5]['temp'],1)),int(round(current_weather['hourly'][5]['feels_like'],1)),current_weather['hourly'][5]['weather'][0]['description'],current_weather['hourly'][6]['dt'],int(round(current_weather['hourly'][6]['temp'],1)),int(round(current_weather['hourly'][6]['feels_like'],1)),current_weather['hourly'][6]['weather'][0]['description'],current_weather['hourly'][7]['dt'],int(round(current_weather['hourly'][7]['temp'],1)),int(round(current_weather['hourly'][7]['feels_like'],1)),current_weather['hourly'][7]['weather'][0]['description'],current_weather['hourly'][8]['dt'],int(round(current_weather['hourly'][8]['temp'],1)),int(round(current_weather['hourly'][8]['feels_like'],1)),current_weather['hourly'][8]['weather'][0]['description'],current_weather['hourly'][9]['dt'],int(round(current_weather['hourly'][9]['temp'],1)),int(round(current_weather['hourly'][9]['feels_like'],1)),current_weather['hourly'][9]['weather'][0]['description'],current_weather['hourly'][10]['dt'],int(round(current_weather['hourly'][10]['temp'],1)),int(round(current_weather['hourly'][10]['feels_like'],1)),current_weather['hourly'][10]['weather'][0]['description'],current_weather['hourly'][11]['dt'],int(round(current_weather['hourly'][11]['temp'],1)),int(round(current_weather['hourly'][11]['feels_like'],1)),current_weather['hourly'][11]['weather'][0]['description'],current_weather['hourly'][12]['dt'],int(round(current_weather['hourly'][12]['temp'],1)),int(round(current_weather['hourly'][12]['feels_like'],1)),current_weather['hourly'][12]['weather'][0]['description'],current_weather['hourly'][13]['dt'],int(round(current_weather['hourly'][13]['temp'],1)),int(round(current_weather['hourly'][13]['feels_like'],1)),current_weather['hourly'][13]['weather'][0]['description'],current_weather['hourly'][14]['dt'],int(round(current_weather['hourly'][14]['temp'],1)),int(round(current_weather['hourly'][14]['feels_like'],1)),current_weather['hourly'][14]['weather'][0]['description'],current_weather['hourly'][15]['dt'],int(round(current_weather['hourly'][15]['temp'],1)),int(round(current_weather['hourly'][15]['feels_like'],1)),current_weather['hourly'][15]['weather'][0]['description'],current_weather['hourly'][16]['dt'],int(round(current_weather['hourly'][16]['temp'],1)),int(round(current_weather['hourly'][16]['feels_like'],1)),current_weather['hourly'][16]['weather'][0]['description'],current_weather['hourly'][17]['dt'],int(round(current_weather['hourly'][17]['temp'],1)),int(round(current_weather['hourly'][17]['feels_like'],1)),current_weather['hourly'][17]['weather'][0]['description'],current_weather['hourly'][18]['dt'],int(round(current_weather['hourly'][18]['temp'],1)),int(round(current_weather['hourly'][18]['feels_like'],1)),current_weather['hourly'][18]['weather'][0]['description'],current_weather['hourly'][19]['dt'],int(round(current_weather['hourly'][19]['temp'],1)),int(round(current_weather['hourly'][19]['feels_like'],1)),current_weather['hourly'][19]['weather'][0]['description'],current_weather['hourly'][20]['dt'],int(round(current_weather['hourly'][20]['temp'],1)),int(round(current_weather['hourly'][20]['feels_like'],1)),current_weather['hourly'][20]['weather'][0]['description'],current_weather['hourly'][21]['dt'],int(round(current_weather['hourly'][21]['temp'],1)),int(round(current_weather['hourly'][21]['feels_like'],1)),current_weather['hourly'][21]['weather'][0]['description'],current_weather['hourly'][22]['dt'],int(round(current_weather['hourly'][22]['temp'],1)),int(round(current_weather['hourly'][22]['feels_like'],1)),current_weather['hourly'][22]['weather'][0]['description'],current_weather['hourly'][23]['dt'],int(round(current_weather['hourly'][23]['temp'],1)),int(round(current_weather['hourly'][23]['feels_like'],1)),current_weather['hourly'][23]['weather'][0]['description'],current_weather['hourly'][24]['dt'],int(round(current_weather['hourly'][24]['temp'],1)),int(round(current_weather['hourly'][24]['feels_like'],1)),current_weather['hourly'][24]['weather'][0]['description']]
					os.environ[unix,current_weather['current']['dt'],int(round(current_weather['current']['temp'],1)),int(round(current_weather['current']['feels_like'],1)),current_weather['current']['weather'][0]['description'],current_weather['hourly'][0]['dt'],int(round(current_weather['hourly'][0]['temp'],1)),int(round(current_weather['hourly'][0]['feels_like'],1)),current_weather['hourly'][0]['weather'][0]['description'],current_weather['hourly'][1]['dt'],int(round(current_weather['hourly'][1]['temp'],1)),int(round(current_weather['hourly'][1]['feels_like'],1)),current_weather['hourly'][1]['weather'][0]['description'],current_weather['hourly'][2]['dt'],int(round(current_weather['hourly'][2]['temp'],1)),int(round(current_weather['hourly'][2]['feels_like'],1)),current_weather['hourly'][2]['weather'][0]['description'],current_weather['hourly'][3]['dt'],int(round(current_weather['hourly'][3]['temp'],1)),int(round(current_weather['hourly'][3]['feels_like'],1)),current_weather['hourly'][3]['weather'][0]['description'],current_weather['hourly'][4]['dt'],int(round(current_weather['hourly'][4]['temp'],1)),int(round(current_weather['hourly'][4]['feels_like'],1)),current_weather['hourly'][4]['weather'][0]['description'],current_weather['hourly'][5]['dt'],int(round(current_weather['hourly'][5]['temp'],1)),int(round(current_weather['hourly'][5]['feels_like'],1)),current_weather['hourly'][5]['weather'][0]['description'],current_weather['hourly'][6]['dt'],int(round(current_weather['hourly'][6]['temp'],1)),int(round(current_weather['hourly'][6]['feels_like'],1)),current_weather['hourly'][6]['weather'][0]['description'],current_weather['hourly'][7]['dt'],int(round(current_weather['hourly'][7]['temp'],1)),int(round(current_weather['hourly'][7]['feels_like'],1)),current_weather['hourly'][7]['weather'][0]['description'],current_weather['hourly'][8]['dt'],int(round(current_weather['hourly'][8]['temp'],1)),int(round(current_weather['hourly'][8]['feels_like'],1)),current_weather['hourly'][8]['weather'][0]['description'],current_weather['hourly'][9]['dt'],int(round(current_weather['hourly'][9]['temp'],1)),int(round(current_weather['hourly'][9]['feels_like'],1)),current_weather['hourly'][9]['weather'][0]['description'],current_weather['hourly'][10]['dt'],int(round(current_weather['hourly'][10]['temp'],1)),int(round(current_weather['hourly'][10]['feels_like'],1)),current_weather['hourly'][10]['weather'][0]['description'],current_weather['hourly'][11]['dt'],int(round(current_weather['hourly'][11]['temp'],1)),int(round(current_weather['hourly'][11]['feels_like'],1)),current_weather['hourly'][11]['weather'][0]['description'],current_weather['hourly'][12]['dt'],int(round(current_weather['hourly'][12]['temp'],1)),int(round(current_weather['hourly'][12]['feels_like'],1)),current_weather['hourly'][12]['weather'][0]['description'],current_weather['hourly'][13]['dt'],int(round(current_weather['hourly'][13]['temp'],1)),int(round(current_weather['hourly'][13]['feels_like'],1)),current_weather['hourly'][13]['weather'][0]['description'],current_weather['hourly'][14]['dt'],int(round(current_weather['hourly'][14]['temp'],1)),int(round(current_weather['hourly'][14]['feels_like'],1)),current_weather['hourly'][14]['weather'][0]['description'],current_weather['hourly'][15]['dt'],int(round(current_weather['hourly'][15]['temp'],1)),int(round(current_weather['hourly'][15]['feels_like'],1)),current_weather['hourly'][15]['weather'][0]['description'],current_weather['hourly'][16]['dt'],int(round(current_weather['hourly'][16]['temp'],1)),int(round(current_weather['hourly'][16]['feels_like'],1)),current_weather['hourly'][16]['weather'][0]['description'],current_weather['hourly'][17]['dt'],int(round(current_weather['hourly'][17]['temp'],1)),int(round(current_weather['hourly'][17]['feels_like'],1)),current_weather['hourly'][17]['weather'][0]['description'],current_weather['hourly'][18]['dt'],int(round(current_weather['hourly'][18]['temp'],1)),int(round(current_weather['hourly'][18]['feels_like'],1)),current_weather['hourly'][18]['weather'][0]['description'],current_weather['hourly'][19]['dt'],int(round(current_weather['hourly'][19]['temp'],1)),int(round(current_weather['hourly'][19]['feels_like'],1)),current_weather['hourly'][19]['weather'][0]['description'],current_weather['hourly'][20]['dt'],int(round(current_weather['hourly'][20]['temp'],1)),int(round(current_weather['hourly'][20]['feels_like'],1)),current_weather['hourly'][20]['weather'][0]['description'],current_weather['hourly'][21]['dt'],int(round(current_weather['hourly'][21]['temp'],1)),int(round(current_weather['hourly'][21]['feels_like'],1)),current_weather['hourly'][21]['weather'][0]['description'],current_weather['hourly'][22]['dt'],int(round(current_weather['hourly'][22]['temp'],1)),int(round(current_weather['hourly'][22]['feels_like'],1)),current_weather['hourly'][22]['weather'][0]['description'],current_weather['hourly'][23]['dt'],int(round(current_weather['hourly'][23]['temp'],1)),int(round(current_weather['hourly'][23]['feels_like'],1)),current_weather['hourly'][23]['weather'][0]['description'],current_weather['hourly'][24]['dt'],int(round(current_weather['hourly'][24]['temp'],1)),int(round(current_weather['hourly'][24]['feels_like'],1)),current_weather['hourly'][24]['weather'][0]['description']] = 'WeatherList'
					os.environ[unix] = 'WeatherList'
				except:
					WeatherList[0] = unix
			screen.fill(settings.bg_color)
			WeatherMapBackground()
			if int(time.strftime("%I", current_time)) >= 10:
				screen.blit(font_size_1.render(TimeList[0],True, settings.font_color), (screen_w*.025,font_size1*.4)) # clock, single-digit hour
			else:
				screen.blit(font_size_1.render(f' {TimeList[0]}',True, settings.font_color), (screen_w*.025,font_size1*.4)) # clock, double-digit hour
			screen.blit(font_size_2.render(TimeList[1],True, settings.font_color), (font_size1*5.5,font_size1*.47)) # AM/PM
			screen.blit(font_size_3.render(f' {TimeList[2]}',True, settings.font_color), (font_size1*5.47,font_size1*1.06)) # CST/CDT
			screen.blit(font_size_2.render(f'{WeatherList[2]}\N{DEGREE SIGN}Real/{WeatherList[3]}\N{DEGREE SIGN}Feel',True, settings.font_color), (screen_w*.025,font_size1*1.6)) # Current Temp
			screen.blit(font_size_2.render(f'{WeatherList[4].title()}',True, settings.font_color), (screen_w*.025,font_size1*2.3)) # Current Sky Condition
			if min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck1: # Check for 'Coat Hat Gloves'
				screen.blit(font_size_2.render(f'{settings.TempAnswer1}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Coat Hat Gloves'
			elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck2: # Check for 'Coat'
				screen.blit(font_size_2.render(f'{settings.TempAnswer2}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Coat'
			elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck3: # Check for 'Long Sleeves'
				screen.blit(font_size_2.render(f'{settings.TempAnswer3}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Long Sleeves'
			elif min (WeatherList[6],WeatherList[7],WeatherList[10],WeatherList[11],WeatherList[14],WeatherList[15],WeatherList[18],WeatherList[19],WeatherList[22],WeatherList[23],WeatherList[26],WeatherList[27],WeatherList[30],WeatherList[31],WeatherList[34],WeatherList[35],WeatherList[38],WeatherList[39]) <= settings.TempCheck4: # Check for 'Short Sleeves'
				screen.blit(font_size_2.render(f'{settings.TempAnswer4}',True, settings.font_color), (screen_w*.025,screen_h*.32)) # Display 'Short Sleeves'
			screen.blit(font_size_3.render(f'Day&Time   Real/Feel   Sky Condition',True, settings.font_color), (screen_w*.525,screen_h/25*0)) # Display column header
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[9]).strftime("%a %#I:%M %p")} {WeatherList[10]}/{WeatherList[11]}\N{DEGREE SIGN}F {WeatherList[12].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*1)) # Hour 02
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[13]).strftime("%a %#I:%M %p")} {WeatherList[14]}/{WeatherList[15]}\N{DEGREE SIGN}F {WeatherList[16].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*2)) # Hour 03
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[17]).strftime("%a %#I:%M %p")} {WeatherList[18]}/{WeatherList[19]}\N{DEGREE SIGN}F {WeatherList[20].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*3)) # Hour 04
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[21]).strftime("%a %#I:%M %p")} {WeatherList[22]}/{WeatherList[23]}\N{DEGREE SIGN}F {WeatherList[24].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*4)) # Hour 05
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[25]).strftime("%a %#I:%M %p")} {WeatherList[26]}/{WeatherList[27]}\N{DEGREE SIGN}F {WeatherList[28].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*5)) # Hour 06
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[29]).strftime("%a %#I:%M %p")} {WeatherList[30]}/{WeatherList[31]}\N{DEGREE SIGN}F {WeatherList[32].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*6)) # Hour 07
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[33]).strftime("%a %#I:%M %p")} {WeatherList[34]}/{WeatherList[35]}\N{DEGREE SIGN}F {WeatherList[36].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*7)) # Hour 08
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[37]).strftime("%a %#I:%M %p")} {WeatherList[38]}/{WeatherList[39]}\N{DEGREE SIGN}F {WeatherList[40].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*8)) # Hour 09
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[41]).strftime("%a %#I:%M %p")} {WeatherList[42]}/{WeatherList[43]}\N{DEGREE SIGN}F {WeatherList[44].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*9)) # Hour 10
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[45]).strftime("%a %#I:%M %p")} {WeatherList[46]}/{WeatherList[47]}\N{DEGREE SIGN}F {WeatherList[48].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*10)) # Hour 11
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[49]).strftime("%a %#I:%M %p")} {WeatherList[50]}/{WeatherList[51]}\N{DEGREE SIGN}F {WeatherList[52].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*11)) # Hour 12
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[53]).strftime("%a %#I:%M %p")} {WeatherList[54]}/{WeatherList[55]}\N{DEGREE SIGN}F {WeatherList[56].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*12)) # Hour 13
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[57]).strftime("%a %#I:%M %p")} {WeatherList[58]}/{WeatherList[59]}\N{DEGREE SIGN}F {WeatherList[60].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*13)) # Hour 14
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[61]).strftime("%a %#I:%M %p")} {WeatherList[62]}/{WeatherList[63]}\N{DEGREE SIGN}F {WeatherList[64].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*14)) # Hour 15
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[65]).strftime("%a %#I:%M %p")} {WeatherList[66]}/{WeatherList[67]}\N{DEGREE SIGN}F {WeatherList[68].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*15)) # Hour 16
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[69]).strftime("%a %#I:%M %p")} {WeatherList[70]}/{WeatherList[71]}\N{DEGREE SIGN}F {WeatherList[72].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*16)) # Hour 17
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[73]).strftime("%a %#I:%M %p")} {WeatherList[74]}/{WeatherList[75]}\N{DEGREE SIGN}F {WeatherList[76].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*17)) # Hour 18
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[77]).strftime("%a %#I:%M %p")} {WeatherList[78]}/{WeatherList[79]}\N{DEGREE SIGN}F {WeatherList[80].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*18)) # Hour 19
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[81]).strftime("%a %#I:%M %p")} {WeatherList[82]}/{WeatherList[83]}\N{DEGREE SIGN}F {WeatherList[84].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*19)) # Hour 20
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[85]).strftime("%a %#I:%M %p")} {WeatherList[86]}/{WeatherList[87]}\N{DEGREE SIGN}F {WeatherList[88].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*20)) # Hour 21
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[89]).strftime("%a %#I:%M %p")} {WeatherList[90]}/{WeatherList[91]}\N{DEGREE SIGN}F {WeatherList[92].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*21)) # Hour 22
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[93]).strftime("%a %#I:%M %p")} {WeatherList[94]}/{WeatherList[95]}\N{DEGREE SIGN}F {WeatherList[96].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*22)) # Hour 23
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[97]).strftime("%a %#I:%M %p")} {WeatherList[98]}/{WeatherList[99]}\N{DEGREE SIGN}F {WeatherList[100].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*23)) # Hour 24
			screen.blit(font_size_3.render(f'{datetime.datetime.fromtimestamp(WeatherList[101]).strftime("%a %#I:%M %p")} {WeatherList[102]}/{WeatherList[103]}\N{DEGREE SIGN}F {WeatherList[104].title()}',True, settings.font_color), (screen_w*.525,screen_h/25*24)) # Hour 25
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
