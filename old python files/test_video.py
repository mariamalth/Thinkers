import pandas as pd
from pyvidplayer import Video
import cv2
from math import hypot
import mediapipe as mp
import pygame
import time
import string
import random
from csv import writer
import pygame
from pygamevideo import Video


pygame.display.set_caption("Jumping Rectangle")

# Initialize Pygame
pygame.init()

# window = pygame.display.set_mode()

# video = Video("background_short.mp4")

# # start video
# video.play()

# # main loop
# while True:
#   ...
#   # draw video to display surface
#   # this function must be called every tick
#   video.draw_to(window, (0, 0))

#   # set window title to current duration of video as hour:minute:second
#   t = video.current_time.format("%h:%m:%s")
#   pygame.display.set_caption(t)


background_image = pygame.image.load("background.png")

### SETTING UP THE GAME
SCREEN_WIDTH = background_image.get_width()
SCREEN_HEIGHT = background_image.get_height()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumping Rectangle")





# Set up the rectangle
RECT_WIDTH = SCREEN_WIDTH * 0.08
RECT_HEIGHT = RECT_WIDTH
center = (SCREEN_WIDTH - RECT_WIDTH) / 2
left = center - SCREEN_WIDTH * 0.18
right = center + SCREEN_WIDTH * 0.18
rect_x = center
rect_y = SCREEN_HEIGHT - RECT_HEIGHT
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)

window = pygame.display.set_mode(video_image.shape[1::-1])
clock = pygame.time.Clock()

run = success
while run:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    success, video_image = video.read()
    if success:
        video_surf = pygame.image.frombuffer(
            video_image.tobytes(), video_image.shape[1::-1], "BGR")
    else:
        run = False
    window.blit(video_surf, (0, 0))
    pygame.draw.rect(screen, (255, 165, 0), (rect_x, rect_y, RECT_WIDTH, RECT_HEIGHT))
    pygame.display.flip()