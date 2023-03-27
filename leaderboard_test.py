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
background_image = pygame.image.load("background.png")

# set up the window
background_image = pygame.image.load("background.png")
WIDTH = background_image.get_width()
HEIGHT = background_image.get_height()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

fps = video.get(cv2.CAP_PROP_FPS)

window = pygame.display.set_mode(video_image.shape[1::-1])
pygame.display.set_caption("Endless Runner")

# set up the colors
WHITE = (255, 255, 255)
GREEN= (0,255,0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
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
font = pygame.font.Font('Dream MMA.ttf',22)
font2 = pygame.font.Font('Dream MMA.ttf',32)

### CODE TO PLAY VIDEO BACKGROUND IN PYGAME WINDOW
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)

window = pygame.display.set_mode(video_image.shape[1::-1])
clock = pygame.time.Clock()


username = None
score = 121

# generating random strings
if username ==None:
    username = ''.join(random.choices(string.ascii_uppercase, k=5))
    user_score = [username,int(score)]
    #!! in the end, this needs to be modified for the leaderboard to store the top 10
    with open('leaderboard.csv', 'a+', newline='\n') as write_obj:
      # Create a writer object from csv module
      csv_writer = writer(write_obj)
      # # Add contents of list as last row in the csv file
      csv_writer.writerow(user_score)
    # print(data)
    # data.loc[len(data)] = user_score
    # print(user_score)
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # print(data)
     

data = data.sort_values(by=['Score'], ascending=False)
data = data.head(10)
# print(data)
usernames = data.loc[:,"Username"]

for row in usernames:
    score = data.loc[data['Username'] == row]['Score'].values
    len_score = len(str(score[0]))
    # print(len_score)

csv_save = data
csv_save.to_csv("leaderboard.csv", index=False)   

#countdown to restart
counter, countdown_seconds = 15, '15'
pygame.time.set_timer(pygame.USEREVENT, 1500)
run = success
while run:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT: 
            counter -= 1
            if counter >= 0:
                countdown_seconds = str(counter)
        if event.type == pygame.QUIT:
            run = False
    
    success, video_image = video.read()
    if success:
        video_surf = pygame.image.frombuffer(
            video_image.tobytes(), video_image.shape[1::-1], "BGR")
        window.blit(video_surf, (0, 0))
        #player lost, show leaderboard
        #here give restart option
        # times = 10000
        # while times >0:
        #     # print(times)

        game_over = font.render(f"game over.. join hands in {countdown_seconds} seconds to restart", True, GREEN)
        #     print(times//1000)
        #     window.blit(video_surf, (0, 0))
        screen.blit(game_over, (WIDTH / 2 - game_over.get_rect().width / 2, HEIGHT / 4))
        
        #     passed_time = clock.tick(120)
        #     times -= passed_time
        # screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
        #order dataset based on highest scores
        data = data.sort_values(by=['Score'], ascending=False)
        # get the top 10 scores 
        data = data.head(10)
        usernames = data.loc[:,"Username"]
        #offset so the rows show one after the other
        offset=0
        for row in usernames:
            score = data.loc[data['Username'] == row]['Score'].values[0]
            leader_row = font.render(f"{row.lower()}.................{str(score)}", True, WHITE)
            screen.blit(leader_row, (WIDTH / 2 - leader_row.get_rect().width / 2, (HEIGHT / 3)+offset))
            offset+=30
    else:
        run = False
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
