import cv2
import numpy as np
import pyautogui

# Set up video capture device
cap = cv2.VideoCapture(0)

# Set up background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2()

# Define initial position of green box to be the center of the screen
box_x = int(pyautogui.size().width/2 -220)
box_y = int(pyautogui.size().height/2 -200)

# Calculate the position of the top-left corner of the green box based on its size
box_w = 50
box_h = 50
box_top_left_x = box_x - int(box_w/2)
box_top_left_y = box_y - int(box_h/2)

# Load background image
bg_img = cv2.imread('background_image.jpg')

while True:
    # Capture frame from video device
    ret, frame = cap.read()
    
    # Apply background subtraction
    fgmask = fgbg.apply(frame)
    
    # Apply thresholding
    thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)[1]
    
    # Find contours in thresholded image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Check if any contours were found
    if len(contours) > 0:
        # Get the largest contour
        c = max(contours, key=cv2.contourArea)
        
        # Get the bounding rectangle for the contour
        x, y, w, h = cv2.boundingRect(c)
        
        # Create copy of background image
        bg_img_copy = bg_img.copy()
        
        # Draw green box around user's movement
        if w > 0:
            # Draw green box in the initial position
            cv2.rectangle(bg_img_copy, (box_top_left_x, box_top_left_y), (box_top_left_x+box_w, box_top_left_y+box_h), (0, 255, 0), -1)
        
        # Update position of green box based on user's movement
        box_x += int(pyautogui.size().width/2 - (x+w/2))
        box_y += int(pyautogui.size().height/2 - (y+h/2))
        
        # Make sure green box stays within bounds of screen
        if box_x < 0:
            box_x = 0
        elif box_x + w > pyautogui.size().width:
            box_x = pyautogui.size().width - w
        if box_y < 0:
            box_y = 0
        elif box_y + h > pyautogui.size().height:
            box_y = pyautogui.size().height - h
    else:
        # If no contours were found, reset position of green box
        box_x = int(pyautogui.size().width/2)
        box_y = int(pyautogui.size().height/2)
        bg_img_copy = bg_img.copy()
        
    # Display the background image with green box
    cv2.imshow('image', bg_img_copy)
    
    # Break loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture device and close all windows
cap.release()

