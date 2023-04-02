import pygame as pg
import cv2
import ptext

#LOOP WORKS
pg.init()
background_image = pg.image.load("linescape_stopmotion/Linescape1.0.0.png")
WIDTH = background_image.get_width()
HEIGHT = background_image.get_height()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
BG_COLOR = pg.Color('gray12')
video = cv2.VideoCapture("background2.mp4")
success, video_image = video.read()
video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fps = video.get(cv2.CAP_PROP_FPS)
duration = video_length/fps

font = pg.font.Font('Pengenalan.ttf',22)
font2 = pg.font.Font('Pengenalan.ttf',32)
font_name = 'Pengenalan.ttf'

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

while i <121:
    images.append(pg.image.load(f"linescape_stopmotion2/background.0.{i}.png"))
    videos.append(cv2.VideoCapture("background2.mp4"))
    i+=1
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
    success, video_image = video.read()
    if success: 
        video_surf = pg.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    window.blit(video_surf, (0, 0))
    if frame_counter == video.get(cv2.CAP_PROP_FRAME_COUNT):
        frame_counter = 0
        video = cv2.VideoCapture("background2.mp4")
    
    text = "hello world"
    text_rect = font.render("hello world", True,WHITE)
    ptext.draw(text, (WIDTH / 2 - text_rect.get_rect().width / 2, HEIGHT / 2), color=WHITE, fontname=font_name, fontsize=32,shadow=(1.5,2.0))
    # screen.fill(BG_COLOR)
    # Blit the current image.
    # screen.blit(image, (0,0))
    # screen.blit(video_surf,(0,0))
    pg.display.flip()
    clock.tick(90)