# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 18:28:11 2023

@author: Ahmed
"""

import cv2
from math import hypot
import mediapipe as mp
import pygame
import time
import string
import random
from csv import writer
import numpy as np
from pyvidplayer import Video
# from protobuf_to_dict import protobuf_to_dict #one potential way to extract landmarks into dictionary
 

### SETTING UP THE GAME

# Initialize Pygame
pygame.init()

background_image = pygame.image.load("background.png")
## video background 
video = cv2.VideoCapture("background2.mp4")

# Set up the screen
SCREEN_WIDTH = background_image.get_width()
SCREEN_HEIGHT = background_image.get_height()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumping Rectangle")
camera = cv2.VideoCapture(0)

# Set up the rectangle
RECT_WIDTH = SCREEN_WIDTH * 0.08
RECT_HEIGHT = RECT_WIDTH
center = (SCREEN_WIDTH - RECT_WIDTH) / 2
left = center - SCREEN_WIDTH * 0.18
right = center + SCREEN_WIDTH * 0.18
rect_x = center
rect_y = SCREEN_HEIGHT - RECT_HEIGHT
rect_vel_y = 0
JUMP_VELOCITY = -10
GRAVITY = 0.5
RECT_CROUCH_HEIGHT = RECT_HEIGHT // 2
is_crouching = False

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

#Set up Data storing mechanisms
username = None
score = 0 

#store landmarks - as a list, can be changed
landmarks = []

# def size(s,b,d):
#     return (d*b) / s
# define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    s_line = 34 / 2
    b_line = 752 / 2
    distance = 370
    side = (distance) / (1-(s_line/b_line))
    speed = 0.5
    def __init__(self, position, style):
        super().__init__()
        self.style = style
        self.position = position
        self.color = self.get_color()
        self.height = self.get_height()
        self.width = self.get_width()
        self.y = self.get_position_y()
        self.x = self.get_position_x()
    
    def get_color(self):
        if self.style == "stand":
            return BLUE
        elif self.style == "crouch":
            return BLACK
        else:
            return GREEN
    # def get_height(self):
    #     initial_size = HEIGHT * 0.01
    #     if self.style == "stand":
    #         return initial_size
    #     else:  # Crouching or Jumping
    #         return initial_size / 2
        
    # def get_width(self):
    #     if self.style == "stand":
    #         return self.height / 2
    #     else:  # Crouching or Jumping
    #         return self.height
    
    # def get_position_y(self):
    #     start_point = HEIGHT - Obstacle.distance - self.height
    #     if self.style == "crouch":
    #         return start_point - self.height
    #     else:  # Standing or jumping
    #         return start_point
    
    # def get_position_x(self):
    #     center_x = WIDTH / 2 - self.width / 2
    #     if self.position == "left":
    #         return center_x - self.width * 3.5
    #     elif self.position == "right":
    #         return center_x + self.width * 3.5
    #     else:  # center
    #         return center_x

    def update(self):
        # start_point = HEIGHT - Obstacle.distance - self.height
        # move the obstacle down the screen
        self.y += Obstacle.speed + self.height / 100 
        # d = (self.y - start_point) + (Obstacle.side - Obstacle.distance)
        # rate = (size(Obstacle.side,Obstacle.b_line,d)) / (Obstacle.s_line)
        # self.height = self.get_height() * rate
        # self.width = self.get_width()
        # self.x = self.get_position_x()
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

### SETTING UP THE MOTION DETECTION

mp_pose = mp.solutions.pose
 
# Setup the Pose function for images.
pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)
 
# Setup the Pose function for videos.
pose_video = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.7,
                          min_tracking_confidence=0.7,enable_segmentation=True)
 
# Initialize mediapipe drawing class.
mp_drawing = mp.solutions.drawing_utils 


def detectPose(image, pose): 
    # Create a copy of the input image.
    output_image = image.copy()
    success, video_image = video.read()
    if success: 
        # video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
        output_image = video_image
    
    background_image = cv2.imread("linescape_stopmotion/Linescape1.0.0.png")
    output_image = background_image
    # Convert the image from BGR into RGB format.
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Perform the Pose Detection.
    results = pose.process(imageRGB)
    # Check if any landmarks are detected and are specified to be drawn.
    if results.pose_landmarks:
        #  print(type(results.pose_landmarks))
        # Draw Pose Landmarks on the output image.
         mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing.DrawingSpec(color=(228,221,19),
                                                                               thickness=0, circle_radius=0),
                                  connection_drawing_spec=mp_drawing.DrawingSpec(color=(228,221,19),
                                                                               thickness=100, circle_radius=2))
         #way of extracting landmarks, data_point is float type
         #can use this loop to add onto landmark list
        #  [
        #     print('x is', data_point.x, 'y is', data_point.y, 'z is', data_point.z,
        #   'visibility is', data_point.visibility)
        #     for data_point in results.pose_landmarks.landmark
        #     ]  
    # mp_drawing.plot_landmarks(results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return output_image, results


def checkHandsJoined(image, results):    
    # Get the height and width of the input image.
    height, width, _ = image.shape
    # Create a copy of the input image to write the hands status label on.
    output_image = image.copy()
    # Get the left wrist landmark x and y coordinates.
    left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * width,
                          results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)

    # Get the right wrist landmark x and y coordinates.
    right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * width,
                           results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
    
    # Calculate the euclidean distance between the left and right wrist.
    euclidean_distance = int(hypot(left_wrist_landmark[0] - right_wrist_landmark[0],
                                   left_wrist_landmark[1] - right_wrist_landmark[1]))
    # Compare the distance between the wrists with a appropriate threshold to check if both hands are joined.
    if euclidean_distance < 130:  
        # Set the hands status to joined.
        hand_status = 'Hands Joined'
    else:   
        # Set the hands status to not joined.
        hand_status = 'Hands Not Joined' 
    
        # Return the output image and the classified hands status indicating whether the hands are joined or not.
    return output_image, hand_status

def checkJumpCrouch(image, results, MID_Y):
    # Get the height and width of the image.
    height, width, _ = image.shape
    
    # Create a copy of the input image to write the posture label on.
    output_image = image.copy()
    
    # Retreive the y-coordinate of the left shoulder landmark.
    left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)
 
    # Retreive the y-coordinate of the right shoulder landmark.
    right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)
 
    # Calculate the y-coordinate of the mid-point of both shoulders.
    actual_mid_y = abs(right_y + left_y) // 2
    
    # Get the left wrist landmark x and y coordinates.
    left_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * height)
 
    # Get the right wrist landmark x and y coordinates.
    right_wrist_landmark = (results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
    
    # Calculate the upper and lower bounds of the threshold.
    lower_bound = MID_Y - SCREEN_WIDTH / 17
    hands_lower_bound = MID_Y - SCREEN_WIDTH / 6
    upper_bound = MID_Y + SCREEN_WIDTH / 8.65
    
    # Check if the person has jumped that is when the y-coordinate of the mid-point 
    # of both shoulders is less than the lower bound.
    if (actual_mid_y < lower_bound) and (right_wrist_landmark < hands_lower_bound and left_wrist_landmark < hands_lower_bound):
        
        # Set the posture to jumping.
        posture = 'Jumping'
    
    # Check if the person has crouched that is when the y-coordinate of the mid-point 
    # of both shoulders is greater than the upper bound.
    elif (actual_mid_y > upper_bound):
        
        # Set the posture to crouching.
        posture = 'Crouching'
    
    # Otherwise the person is standing and the y-coordinate of the mid-point 
    # of both shoulders is between the upper and lower bounds.    
    else:
        
        # Set the posture to Standing straight.
        posture = 'Standing'
        
 
        # Return the output image and posture indicating whether the person is standing straight or has jumped, or crouched.
    return output_image, posture
    

def checkLeftRight(image, results):

    # Declare a variable to store the horizontal position (left, center, right) of the person.
    horizontal_position = None
    
    # Get the height and width of the image.
    height, width, _ = image.shape
    
    # Create a copy of the input image to write the horizontal position on.
    output_image = image.copy()
    
    # Retreive the x-coordinate of the left shoulder landmark.
    left_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width)

    # Retreive the x-corrdinate of the right shoulder landmark.
    right_x = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width)
    
    # Check if the person is at left that is when both shoulder landmarks x-corrdinates
    # are less than or equal to the x-corrdinate of the center of the image.
    margin = SCREEN_WIDTH / 10
    left_boundry = width//2 - margin
    right_boundry = width//2 + margin
    if (right_x <= left_boundry and left_x <= left_boundry):
        
        # Set the person's position to left.
        horizontal_position = 'Left'

    # Check if the person is at right that is when both shoulder landmarks x-corrdinates
    # are greater than or equal to the x-corrdinate of the center of the image.
    elif (right_x >= right_boundry and left_x >= right_boundry):
        
        # Set the person's position to right.
        horizontal_position = 'Right'
    
    # Check if the person is at center that is when right shoulder landmark x-corrdinate is greater than or equal to
    # and left shoulder landmark x-corrdinate is less than or equal to the x-corrdinate of the center of the image.
    # elif (right_x >= width//2 and left_x <= width//2):
    else:
        
        # Set the person's position to center.
        horizontal_position = 'Center'
        

        # Return the output image and the person's horizontal position.
    return output_image, horizontal_position


camera_video = cv2.VideoCapture(0)
camera_video.set(3,1280)
camera_video.set(4,960)
 
 
# Initialize a variable to store the time of the previous frame.
time1 = 0
 
# Initialize a variable to store the state of the game (started or not).
game_started = False   
 
# Initialize a variable to store the index of the current horizontal position of the person.
# At Start the character is at center so the index is 1 and it can move left (value 0) and right (value 2).
x_pos_index = 1
 
# Initialize a variable to store the index of the current vertical posture of the person.
# At Start the person is standing so the index is 1 and he can crouch (value 0) and jump (value 2).
y_pos_index = 1
 
# Declate a variable to store the intial y-coordinate of the mid-point of both shoulders of the person.
MID_Y = None
 
# Initialize a counter to store count of the number of consecutive frames with person's hands joined.
counter = 0
 
# Initialize the number of consecutive frames on which we want to check if person hands joined before starting the game.
num_of_frames = 10


# Set up the game loop
clock = pygame.time.Clock()

# Game loop
while camera_video.isOpened():
    
    movement = None
    
    # Read a frame.
    ok, frame = camera_video.read()
    
    # Check if frame is not read properly then continue to the next iteration to read the next frame.
    if not ok:
        continue
    
    # Flip the frame horizontally for natural (selfie-view) visualization.
    frame = cv2.flip(frame,1)
    
    # Get the height and width of the frame of the webcam video.
    frame_height, frame_width, _ = frame.shape
    
    # Perform the pose detection on the frame.
    frame, results = detectPose(frame, pose_video)

    
    # Check if the pose landmarks in the frame are detected.
    if results.pose_landmarks:
        
        # Check if the game has started
        if game_started:    
            # Get horizontal position of the person in the frame.
            frame, horizontal_position = checkLeftRight(frame, results)
            
            # Check if the person has moved to left from center or to center from right.
            if (horizontal_position=='Left' and x_pos_index!=0) or (horizontal_position=='Center' and x_pos_index==2):
                
                # Press the left arrow key.
                movement = "left"
                
                # Update the horizontal position index of the character.
                x_pos_index -= 1               
 
            # Check if the person has moved to Right from center or to center from left.
            elif (horizontal_position=='Right' and x_pos_index!=2) or (horizontal_position=='Center' and x_pos_index==0):
                
                # Press the right arrow key.
                movement = "right"
                
                # Update the horizontal position index of the character.
                x_pos_index += 1
            
            #--------------------------------------------------------------------------------------------------------------
        
        # Otherwise if the game has not started    
        else:
            
            # Write the text representing the way to start the game on the frame. 
            cv2.putText(frame, 'JOIN BOTH HANDS TO START THE GAME.', (5, frame_height - 10), cv2.FONT_HERSHEY_PLAIN,
                        2, (0, 255, 0), 3)
        
        # Command to Start or resume the game.
        #------------------------------------------------------------------------------------------------------------------
        
        # Check if the left and right hands are joined.
        if checkHandsJoined(frame, results)[1] == 'Hands Joined':
 
            # Increment the count of consecutive frames with +ve condition.
            counter += 1
 
            # Check if the counter is equal to the required number of consecutive frames.  
            if counter == num_of_frames:
 
                # Command to Start the game first time.
                #----------------------------------------------------------------------------------------------------------
                
                # Create randomly generated username for player

                # generating random strings
                if username ==None:
                    username = ''.join(random.choices(string.ascii_uppercase, k=5))
                    user_score = [username,score]


                    #STORING TEST -> this will be moved to a place where it stores row after user loses last life
                    # -> should also check if user score makes it to leaderboard
                    # with open('leaderboard.csv', 'a+', newline='\n') as write_obj:
                    #  # Create a writer object from csv module
                    #  csv_writer = writer(write_obj)
                    #  # Add contents of list as last row in the csv file
                    #  csv_writer.writerow(user_score)
                                    
                #--------------------------------------------------------------------------------------------------------------
                # Check if the game has not started yet.
                if not(game_started):
 
                    # Update the value of the variable that stores the game state.
                    game_started = True
 
                    # Retreive the y-coordinate of the left shoulder landmark.
                    left_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame_height)
 
                    # Retreive the y-coordinate of the right shoulder landmark.
                    right_y = int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame_height)
 
                    # Calculate the intial y-coordinate of the mid-point of both shoulders of the person.
                    MID_Y = abs(right_y + left_y) // 2
                
                #--------------------------------------------------------------
                
                # Update the counter value to zero.
                counter = 0
 
        # Otherwise if the left and right hands are not joined.        
        else:
 
            # Update the counter value to zero.
            counter = 0
            
        #------------------------------------------------------------------------------------------------------------------
 
        # Commands to control the vertical movements of the character.
        #------------------------------------------------------------------------------------------------------------------
        
        # Check if the intial y-coordinate of the mid-point of both shoulders of the person has a value.
        if MID_Y:
            
            # Get posture (jumping, crouching or standing) of the person in the frame. 
            frame, posture = checkJumpCrouch(frame, results, MID_Y)
            
            # Check if the person has jumped.
            if posture == 'Jumping' and y_pos_index == 1:
 
                # Press the up arrow key
                movement = "up"
                
                # Update the veritcal position index of  the character.
                y_pos_index += 1 
 
            # Check if the person has crouched.
            elif posture == 'Crouching' and y_pos_index == 1:
 
                # Press the down arrow key
                movement = "down"
                
                # Update the veritcal position index of the character.
                y_pos_index -= 1
            
            # Check if the person has stood.
            elif posture == 'Standing' and y_pos_index   != 1:
                
                # Update the veritcal position index of the character.
                y_pos_index = 1
        
        #------------------------------------------------------------------------------------------------------------------
    
    
    # Otherwise if the pose landmarks in the frame are not detected.       
    else:
 
        # Update the counter value to zero.
        counter = 0
        
    
    # Display the frame.            
    cv2.imshow('Immersive Fitness Experience', frame)
    
    # Wait for 1ms. If a a key is pressed, retreive the ASCII code of the key.
    k = cv2.waitKey(1)
    
    # Check if 'ESC' is pressed and break the loop.
    if(k == 27):
        break

    if is_crouching:
        time.sleep(0.8)
        RECT_HEIGHT = RECT_CROUCH_HEIGHT * 2
        is_crouching = False

    if movement == "up":
        rect_vel_y = JUMP_VELOCITY
    elif movement == "left":
         if rect_x == center:
             rect_x = left
         elif rect_x == right:
             rect_x = center
    elif movement == "right":
         if rect_x == left:
             rect_x = center
         elif rect_x == center:
             rect_x = right
    elif movement == "down":
        is_crouching = True
        RECT_HEIGHT = RECT_CROUCH_HEIGHT
       

    # Update the rectangle
    rect_y += rect_vel_y
    rect_vel_y += GRAVITY

    # Check for collision with the ground
    if rect_y + RECT_HEIGHT > SCREEN_HEIGHT:
        rect_y = SCREEN_HEIGHT - RECT_HEIGHT
        rect_vel_y = 0
        
    
    # Draw the screen
    screen.blit(background_image, (0, 0))
    # ret, frame = camera.read()
		
    # screen.fill([0,0,0])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame, axes=(1,0))
    frame = np.flip(frame,1)
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0,0))

    if results.segmentation_mask is not None: 
         rgb = cv2.cvtColor(results.segmentation_mask, cv2.COLOR_GRAY2RGB)
         rgb = rgb * 255
         rgb = rgb.astype(np.uint8)
        #  screen.blit(rgb)

    pygame.draw.rect(screen, (255, 165, 0), (rect_x, rect_y, RECT_WIDTH, RECT_HEIGHT))
    pygame.display.update()

    # # Limit the frame rate
    # clock.tick(100)

# Clean up Pygame
pygame.quit()
