import pygame as pg
import cv2
import ptext
import random
from PIL import Image

#LOOP WORKS

pg.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

pg.mixer.init()

pg.mixer.music.load('background.mp3')

pg.mixer.music.play(-1)
pg.init()
background_image = pg.image.load("background.png")
WIDTH = background_image.get_width()
HEIGHT = background_image.get_height()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
BG_COLOR = pg.Color('gray12')


environments = ["oceanscape.mp4","desertscape.mp4","mountainscape.mp4"]
start_environment = random.choice(environments)
video = cv2.VideoCapture(start_environment)
success, video_image = video.read()
video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fps = video.get(cv2.CAP_PROP_FPS)
duration = video_length/fps

font = pg.font.Font('blade.ttf',22)
font2 = pg.font.Font('blade.ttf',32)
font_name = 'blade.ttf'

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

frame_counter = 0 
# print(duration)

window = pg.display.set_mode(video_image.shape[1::-1])
i = 0
images = []
videos = []

success, video_image = video.read()
if success: 
    video_surf = pg.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
window.blit(video_surf, (0, 0))

# while i <121:
#     images.append(pg.image.load(f"linescape_stopmotion2/background.0.{i}.png"))
#     videos.append(cv2.VideoCapture("background2.mp4"))
#     i+=1
# Three differently colored surfaces for demonstration purposes.
# for color in ((0, 100, 200), (200, 100, 50), (100, 200, 0)):
#     surface = pg.Surface((200, 100))
#     surface.fill(color)
#     images.append(surface)

# index = 0
# image = images[index]
# # Define a new event type.
# CHANGE_IMAGE_EVENT = pg.USEREVENT + 1
# # Add the event to the event queue every 1000 ms.
# pg.time.set_timer(CHANGE_IMAGE_EVENT, 15)

done = False
while True:
    frame_counter += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        # elif event.type == CHANGE_IMAGE_EVENT:
        #     # Increment the index, use modulo len(images)
        #     # to keep it in the correct range and change
        #     # the image.
        #     index += 1
        #     index %= len(images)
        #     image = images[index]  # Alternatively load the next image here.

        #video will be constantly playing, tutorial or not.
    # start_environment = random.choice(environments)
    # video = cv2.VideoCapture(start_environment)
    success, video_image = video.read()
    if success: 
        video_surf = pg.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    screen.blit(video_surf, (0, 0))
    
    #video loop 
    if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        start_environment = random.choice(environments)
        # print("??????????????????",start_environment)
        video = cv2.VideoCapture(start_environment)
        # print(video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_counter = 0

    
    explain = "these are the different obstacles you will see \nand what action they mean"
    explain_rect = font.render(f"{explain}", True,WHITE)
    ptext.draw(explain, (WIDTH /2 - explain_rect.get_rect().width / 2.5, HEIGHT / 10), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))
    
    style = ["stand","jump","crouch"]
    position = "center"
    #loop through each style to get the image of each obstacle
    for i in range(len(style)):
        if start_environment == "oceanscape.mp4" and style[i] == "jump":
            img_style = "crouch"
        else:
            img_style = style[i]
        img_file = f"{start_environment.replace('.mp4','')}_{img_style}.jpg"
        img = Image.open(img_file)
        r = 15/img.size[1]
        initial_width = img.size[0] * r 
        initial_height = img.size[1] * r

        # resize image
        pic_width = 300
        pic_height = 150
        pos = (WIDTH / 2) - (pic_width/2)
        if style[i] == "stand":
            pos = 50
            pic_width = 200
            pic_height = 175
        if style[i] == "crouch": 
            pos = WIDTH - 350
        img_resized = img.resize((pic_width, pic_height))
        # Convert the resized image to a Pygame surface and blit it
        cube = pg.image.frombuffer(img_resized.tobytes(), img_resized.size, "RGBA")
        screen.blit(cube, (pos, HEIGHT /2.5 ))
        
        #print the corresponding text below it
        obs_type = ["move","squat","jump"]
        text = f"{obs_type[i]}"
        text_rect = font.render(f"{obs_type[i]}", True,WHITE)
        ptext.draw(text, (pos+(pic_width/4), HEIGHT / 1.5), color=WHITE, fontname=font_name, fontsize=30,shadow=(1.5,2.0))
    # text = "hello world"
    # text_rect = font.render("hello world", True,WHITE)
    # ptext.draw(text, (WIDTH / 2 - text_rect.get_rect().width / 2, HEIGHT / 2), color=WHITE, fontname=font_name, fontsize=32,shadow=(1.5,2.0))
    # screen.fill(BG_COLOR)
    # Blit the current image.
    # screen.blit(image, (0,0))
    # screen.blit(video_surf,(0,0))
    pg.display.flip()
    clock.tick(90)