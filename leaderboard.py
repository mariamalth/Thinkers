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


data = pd.read_csv("leaderboard.csv")
data = data.sort_values(by=['Score'], ascending=False)
data = data.head(10)
print(data)
usernames = data.loc[:,"Username"]

for row in usernames:
    score = data.loc[data['Username'] == row]['Score'].values

csv_save = data
csv_save.to_csv("leaderboard.csv", index=False)

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

# Initialize Pygame
pygame.init()

### CODE TO PLAY VIDEO BACKGROUND IN PYGAME WINDOW
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


### OTHER WAY TO PLAY VIDEO - shows on separate window
# import moviepy.editor

# pygame.init()
# video = moviepy.editor.VideoFileClip("background.mp4")
# video.preview()
# pygame.quit()


# data = pd.read_csv("leaderboard.csv")
# data = data.to_json(orient="columns") 
# print(data['Username'][0])
# print(data['Username'])

# usernames = data.loc[:,"Username"]
# print(usernames)

# for row in usernames:
#     score = data.loc[data['Username'] == row]['Score'].values[0]
    # print(f"Username = {row}, score = "+str(score))


# test = 'SLDDK'
# print(data.query('Username == @test')['Score'])
# print("-----------------------------------------")
# print()
