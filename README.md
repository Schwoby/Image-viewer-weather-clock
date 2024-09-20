# Image Viewer Weather Clock
Initially created for my children to know what clothing was acceptable for the day. Written in Python3 using PyGame for the display. Written for use in Linux; some variances, which i will attempt to notate, will need to be made for Windows. Any and all Mac versions of OS have been untested.

## Version History
### V5
- Added error handeling to provid graceful fail conditions
  - Weather web pulls
  - Removing images from image folder
  - Skipping non-image files
- [ ] Various bug fixes - solve unknown/new issues
  - OpenWeather API changed, updated code to match. Weather forcast information is now only accessable via their "Base plan", which a credit card is required for, but the first 1000 calls per day are free.
- [ ] scale clock with screen resolution (for better cross-device consistency)
### V4
- **Initial upload of code**
- Rewrote image viewer code (now in PyGame)
- Updated how the image set diplay order is generated and accessed
- Added image info display in the top left
- Fixed some timing bugs for switching between the image viewer and the weather clock
### V3
- Added the image viewer (originally in Turtle)
- Fixed bugs from mismatched display viewers (PyGame vs Turtle)
- Added time breaks to switch between the image viewer and the weather clock
### V2
- Adjusted spacing for exsisting content, no exsisting content removed
- Added weather foract on right size of screen
- Added weather map to bottom left of screen
- Added clothing minimum requirements
### V1
- Clock and current weather, full screen using PyGame

## Modes of Operation
### Weather
#### Weather & Clock (home.openweathermap.org)
Starting off with the weather clock, this will show the current time and weather in the top left quarter of the screen.
#### Weather & Clock Outlook
based on the next eight (8) hours of forcasted tempratures, this clock section will show the minimum accepted clothing.
#### Weather Forecast (home.openweathermap.org)
On the right half of the screen, a weather outlook is provided for the next 24 hours.
#### Weather Map (for USA) (radar.weather.gov)
On the bottom left quarter of the screen, a series of map images with the most recent weather analysis will be shown, a different image each second in ten (10) second rounds, restarting when the second ends in zero (0).
### Image Viewer
#### Analog Clock
This clock is programed to move each of the three (3) hands the appropre space once every second. Displayed in the bottom left corner
#### Image Info
The image info is obtained by parsing the image name. The naming format is "[Artist Name] - [Year(s)] - [Image Name].[image extention]". The info is parsed with the space-hyphen-space between each name set; this alows for hyphens to be used within the names and years, so long as its directly between alphanumeric characters on each side.
#### Image
The image set display order will be created fresh each round by scanning the image folder for all images and then randomizing this list. If the image viewer is inturupted to display the Weather, it will resume where it left off in the image set. At the end of the image set, it will rescan the image folder and reindex the images it finds. The image will fit to the screen while retaining it's hight/width ratio.
