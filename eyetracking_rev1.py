# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 00:36:16 2021

@author: titan
"""

import cv2 as cv
import numpy as np
import dlib       #libaray to detect points on face
import pyautogui   # control mouse and keyboard
import imutils     #for finding contour
import keyboard     #detect keypress


cx_L = 0                                     
cy_L = 0
cx_R = 0           #declare variables for center point of eyes contour
cy_R = 0

conx = 0
cony = 0
area = 0        #more vairables, etc
olddm=0
newm=0

was_pressed = False

def nothing(x):      #function that do thing, use for trackbar
    pass             

def midpoint(p1,p2):                                 #find a point in the middle of 2 points    
    return int((p1.x+p2.x)/2),int((p1.y+p2.y)/2)                 #basic pythagoras formula

def left_eye():           #detect left eye
    x = cv.getTrackbarPos("threshold", "frame")      #get trackbar position
    Leye = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                         (landmarks.part(37).x, landmarks.part(37).y), 
                         (landmarks.part(38).x, landmarks.part(38).y),                #array of points covering the left eye, using a module from dlib
                         (landmarks.part(39).x, landmarks.part(39).y), 
                         (landmarks.part(40).x, landmarks.part(40).y), 
                         (landmarks.part(41).x, landmarks.part(41).y)],np.int32)
        
    min_x = np.min(Leye[:,0])
    max_x = np.max(Leye[:,0])
    min_y = np.min(Leye[:,1])       #find the maximum and minimum in x axis and y axis  from the array
    max_y = np.max(Leye[:,1])
    
    udratio = (max_y/min_y)
    
    
    eye = frame[min_y:max_y,min_x:max_x]          #crop to get only the left eye frame
    eye =cv.resize(eye,None,fx = 10,fy=10)         #resize the left eye frame
    eye = cv.cvtColor(eye,cv.COLOR_BGR2GRAY)        #convert to gray
    eye = cv.GaussianBlur(eye, (15, 15), 5)        #gaussian blur
    row_e,col_e = eye.shape                        #get row and column
    eye =eye[0:row_e,int(col_e/5.5):col_e] 
    eye =eye[0:row_e,0:int(col_e*4.3/6)]          #crop unwanted section
    eye[0:int(row_e/6),0:col_e]= 255 
    row_e,col_e = eye.shape                       #get row and column again after cropping
    rowpad = 250-row_e
    colpad = 400-col_e
    
        
 
    eye = cv.copyMakeBorder(eye, 0, rowpad, 0, colpad, cv.BORDER_CONSTANT)      #add padding
    
  
    ret,thresh = cv.threshold(eye,x,255,cv.THRESH_BINARY)           #binary threshhold
    #cv.imshow('eyepad',eye1)
    thresh = 255-thresh           #inversion,  from white background to black background (contour doesn't work on white background, it will detect white color)
    kernel = np.ones((7,7),np.uint8)      #kernel for morphology
    thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel,iterations = 7)    #morphology closing
    #thresh = cv.copyMakeBorder(thresh, 0, rowpad, 0, colpad, cv.BORDER_CONSTANT)
    mask = np.zeros((250,400),np.uint8)           #create mask for ellipse, same size as the left eye frame4
    mask_mid_x = int(col_e/2)
    mask_mid_y = int(row_e/2)
    if mask_mid_x-20 < 0  or mask_mid_y - 30 <0:
        mask_mid_x = 21
        mask_mid_y = 31
        
    cv.ellipse(mask, (mask_mid_x,mask_mid_y), (mask_mid_x-20,mask_mid_y-30), 0, 0, 360,255,-1)     #create ellipse on the mask
    
    thresh = cv.multiply(mask, thresh)      #merge the threshhold and the ellipse to cut out the corner
    
    
    return thresh,eye,udratio

def right_eye():            # same as left eye function
    x = cv.getTrackbarPos("threshold", "frame")
    Leye = np.array([(landmarks.part(42).x, landmarks.part(42).y),
                         (landmarks.part(43).x, landmarks.part(43).y), 
                         (landmarks.part(44).x, landmarks.part(44).y), 
                         (landmarks.part(45).x, landmarks.part(45).y), 
                         (landmarks.part(46).x, landmarks.part(46).y), 
                         (landmarks.part(47).x, landmarks.part(47).y)],np.int32)
        
    min_x = np.min(Leye[:,0])
    max_x = np.max(Leye[:,0])
    min_y = np.min(Leye[:,1])
    max_y = np.max(Leye[:,1])
    
    udratio = (max_y/min_y)
  
    
    
    eye = frame[min_y:max_y,min_x:max_x]
    eye =cv.resize(eye,None,fx = 10,fy=10)
    
    eye = cv.cvtColor(eye,cv.COLOR_BGR2GRAY)  
    eye = cv.GaussianBlur(eye, (15, 15), 5)
    row_e,col_e = eye.shape
    eye =eye[0:row_e,int(col_e/5.5):col_e] 
    eye =eye[0:row_e,0:int(col_e*4.3/6)] 
    eye[0:int(row_e/6),0:col_e]= 255
    row_e,col_e = eye.shape
    rowpad = 250-row_e
    colpad = 400-col_e    
    
    eye = cv.copyMakeBorder(eye, 0, rowpad, 0, colpad, cv.BORDER_CONSTANT)
    ret,thresh = cv.threshold(eye,x,255,cv.THRESH_BINARY)
    
    thresh = 255-thresh
    kernel = np.ones((9,9),np.uint8)
    thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel,iterations = 7)
    
    mask = np.zeros((250,400),np.uint8)     
    mask_mid_x = int(col_e/2)
    mask_mid_y = int(row_e/2)
    if mask_mid_x-20 < 0  or mask_mid_y - 30 <0:
        mask_mid_x = 21
        mask_mid_y = 31      
    cv.ellipse(mask, (mask_mid_x,mask_mid_y), (mask_mid_x-20,mask_mid_y-30), 0, 0, 360,255,-1)   
    
    thresh = cv.multiply(mask, thresh)     
    
    
    
    
    
    return thresh,eye ,udratio

def left_eye_blink():      #detect if the left eye is blinking
    _,ctop = midpoint(landmarks.part(37), landmarks.part(38))        #find the middle of the top part of the eye
    _,cbottom = midpoint(landmarks.part(41), landmarks.part(40))      #find the middle of the bottom part of the eye
    
    
    hlen = landmarks.part(39).x - landmarks.part(36).x        #find the horizontal length of the eye
    vlen = ctop - cbottom                                    #find the virtical length of the eye
    blinkratio = (vlen/hlen) *-1                             #find the ratio of both, multiply -1 to get positive number
    return blinkratio

def right_eye_blink():    #same as left eye blink function
    _,ctop = midpoint(landmarks.part(43), landmarks.part(44))
    _,cbottom = midpoint(landmarks.part(47), landmarks.part(46))
    
    
    hlen = landmarks.part(45).x - landmarks.part(42).x
    vlen = ctop - cbottom
    blinkratio = (vlen/hlen) *-1 
    return blinkratio



def contour(x,y):    #draw contour and find the center point of the contour
    global conx  
    
    global cony      #set variable as global so we can return it from inside the if condition\
    
    global area
 
    cnst = cv.findContours(x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)        
    cnst = imutils.grab_contours(cnst)                                   #find and grab contour
    
    for c in cnst:
            area = cv.contourArea(c)                          #area of the contour
            
            
            if area>5000: 
                #cv.putText(frame, 'eye detected', (50,100), cv.FONT_HERSHEY_COMPLEX,5, (0,255,0),3)
        
                cv.drawContours(y, [c],-1, (0,255,0), 2)            
                M = cv.moments(c)
                #row,col = x.shape                         #draw the contour and draw a circle dot at the center point of the contour
             
                conx = int(M['m10']/M['m00'])
                cony = int(M['m01']/M['m00'])
                
                #cv.circle(x,(conx,cony),7,(0,0,0),-1)
    return conx,cony ,area    # return the coordinate of the center point of the contourmi




#main

pyautogui.FAILSAFE = False        #failsafe off to pervent this program from stopping due to error



detector = dlib.get_frontal_face_detector()           #get the face detector from dlib
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")       #get the trained data that will detect the face

cap = cv.VideoCapture(0)      #set camera      
cv.namedWindow('frame',cv.WINDOW_FREERATIO)    #create windows
cv.createTrackbar("threshold", "frame", 50, 255, nothing)      #create trackbar
#cv.createTrackbar("mouse position offset", "frame", 1, 120, nothing)

leftdot = cv.imread('leftdot.png')
rightdot = cv.imread('rightdot.png')
updot = cv.imread('updot.png')                      #import images that will be used for calibration
downdot = cv.imread('downdot.png')
startmouse = cv.imread('startmouse.png')




x = 0
p = 0           #variables for if, while loop
m = 0
cx_min =0
cx_max = 0                  
cy_min = 0          #variables for maximum and minimum range that the eyes can gaze at on both x and y axis
cy_max = 0

while True:      
    u = 0               #variable for switching windows
    _,frame = cap.read()                    #read webcam
    gray = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)         #convert bgr to gray
    faces = detector(gray)                          #detect face from camera
    #frame = cv.copyMakeBorder(frame, 0,0, 30,30, cv.BORDER_ISOLATED)
    frame1 = frame.copy()               #make a copy
    frame1 = cv.copyMakeBorder(frame1, 0,0, 30,30, cv.BORDER_DEFAULT)       #add padding
    frame1 = cv.copyMakeBorder(frame1, 0,480,0,0, cv.BORDER_CONSTANT)       #add more padding
    cv.putText(frame1, 'face not found', (160,700), cv.FONT_HERSHEY_PLAIN,3 ,(0,255,0),3)
    cv.putText(frame1, 'press ENTER to exit', (230,750), cv.FONT_HERSHEY_PLAIN,1.5,(0,255,0),2)         #put text
    for face in faces:            #do a fuction for a single face
        faceleft,facetop,faceright,facebottom = face.left(),face.top(),face.right(),face.bottom()       #detect left,up,right and down side of the face to form a rectangle over the face
        cv.rectangle(frame, (faceleft,facetop), (faceright,facebottom), (0,255,0),2)   #rectangle over the detected face
        cv.putText(frame, 'face', (faceleft,facetop-10), cv.FONT_HERSHEY_PLAIN,1.5 ,(0,255,0),1)      #text on the rectangle
        landmarks = predictor(gray,face)            #locate landmark points on the face

        thresh_L,eye_L,udratio_L = left_eye()
        blinkratio_L             = left_eye_blink()
        thresh_R,eye_R,udratio_R = right_eye()          #call function
        blinkratio_R             = right_eye_blink()
        cx_L,cy_L,area_L         = contour(thresh_L, eye_L)
        cx_R,cy_R,area_R         = contour(thresh_R, eye_R)
        
       
        
        
        
        thresheye = cv.hconcat([thresh_L,thresh_R])         #merge 2 frames
        thresheye = cv.merge((thresheye,thresheye,thresheye))    #merge to convert grayscale to rgb channel
        cv.circle(thresheye,(cx_L,cy_L),7,(0,0,255),-1)         
        cv.circle(thresheye,(cx_R+400,cy_R),7,(0,0,255),-1)     #circle the pupils
        
       
        eye = cv.hconcat([eye_L,eye_R])     #merge 2 frames
        eye = cv.merge((eye,eye,eye))       #convert gray channel to rgb channel so that it can merge with other rgb frame
        cv.circle(eye,(cx_L,cy_L),70,(0,0,255),3)
        cv.circle(eye,(cx_R+400,cy_R),70,(0,0,255),3)       #circle the pupils
       
      
        eyes = cv.vconcat([eye,thresheye])              #merge 2 frames
        row_eyes , col_eyes,_ = eyes.shape              #check get the size of the frame
    
        cv.line(eyes,(400,0), (400,700), (255,255,255),1)       
        cv.line(eyes,(0,250), (900,250), (255,255,255),1)   #add line to define each smaller windows
        cv.putText(eyes, 'left eye', (280,230), cv.FONT_HERSHEY_PLAIN,1.5, (255,255,255),1)     
        cv.putText(eyes, 'right eye', (570,230), cv.FONT_HERSHEY_PLAIN,1.5, (255,255,255),1)                #put titles for the smaller windows
        cv.putText(eyes, 'right eye threshold', (440,450), cv.FONT_HERSHEY_PLAIN,1.5, (255,255,255),1)
        cv.putText(eyes, 'left eye threshold', (150,450), cv.FONT_HERSHEY_PLAIN,1.5, (255,255,255),1)
       
        frame = cv.copyMakeBorder(frame, 0,0, 30,30, cv.BORDER_DEFAULT)     #add padding
        eyes = eyes[0:480,0:700,:]          #cut the frame
        
        frame = frame[0:480,0:700,:]            #cut more frame
        frame = cv.vconcat([frame,eyes])        #merge frames
        
        
        
      
        avg_x = int(((cx_L+cx_R)/-2)+300)                         #find average of the eyes's location on the x axis
  
        avg_y = int(((udratio_L+udratio_R)/2)*10000-10000)          #find average of the eyes's location on the y axis
  
        if keyboard.is_pressed('d'):        #reset/start over
            m=0
            cv.destroyWindow('ye')
        if m == 0:
            cv.putText(frame, 'adjust the threshold so that it detects a pupil', (10,30), cv.FONT_HERSHEY_PLAIN,1.5,(0,255,0),2)
            cv.putText(frame, 'then press S to start calibrate', (10,60), cv.FONT_HERSHEY_PLAIN,1.5,(0,255,0),2)
        ##############################    
        if keyboard.is_pressed('s'):
            if not was_pressed:
                m += 1
                was_pressed = True      #keyboard press function 
        else:                           #when press 's' m will +1
            was_pressed = False         #if we don't use this function, when we press 's', the program will count every milisecond and add that to m vairable
        ############################                                               (for example, press s once and m will jump from 0 to 500 instead of 0 to 1)
        if m ==1:
            cv.namedWindow('ye',cv.WINDOW_FULLSCREEN)
            cv.imshow('ye',leftdot)                 #start calibration and show the calibration screen
        
        if m ==2:
            cx_min= avg_x
            print("cx_min"+str(cx_min))         #save the eyes location when user looking at the left side of the screen
            #cy_min = avg_y
            m=3
            
            
            
        if m==3:
            cv.putText(frame, 'look at the right edge of screen and press S', (10,30), cv.FONT_HERSHEY_PLAIN,1.7 ,(0,255,0),2) 
            cv.imshow('ye',rightdot)            #put instruction for user
           
        if m ==4:         
            cx_max= avg_x
            print("cx_max"+str(cx_max))      #save the eyes location when user looking at the right side of the screen
            #cy_max = avg_y
            m=5
            
        if m==5:
            cv.putText(frame, 'look at the upper edge of screen and press S', (10,30), cv.FONT_HERSHEY_PLAIN,1.7 ,(0,255,0),2)
            cv.imshow('ye',updot)
        if m ==6:       
            cy_min = avg_y
            print("cy_min"+str(cy_min))          #save the eyes location when user looking at the upper side of the screen
            m=7
            
        if m==7:
            cv.putText(frame, 'look at the lower edge of screen and press S', (10,30), cv.FONT_HERSHEY_PLAIN,1.7 ,(0,255,0),2)
            cv.imshow('ye',downdot)
        if m ==8:       
            cy_max = avg_y                       #save the eyes location when user looking at the lower side of the screen
            print("cy_max"+str(cy_max))
            m=9
        
        if m ==9:
            cv.imshow('ye',startmouse)          #ask if to start mouse control
            
        if m ==10:
            cv.destroyWindow('ye')              #close calibration screen
           
            NewValueY = (((avg_y - cy_min) * (1080 - 0)) / (cy_max - cy_min)) + 0       #convert number range to screen size
            
            NewValueX = (((avg_x - cx_min) * (1920 - 0)) / (cx_max - cx_min)) + 0
            
            
            cv.putText(frame, 'calibration completed', (2,30), cv.FONT_HERSHEY_PLAIN,1.5 ,(0,255,0),2)
            cv.putText(frame, 'mouse control activated', (2,60), cv.FONT_HERSHEY_PLAIN,1.5 ,(0,255,0),2)            #show text
            cv.putText(frame, 'press D to start over ', (2,120), cv.FONT_HERSHEY_PLAIN,1.5 ,(0,255,0),2)
            cv.putText(frame, 'press ENTER to exit', (2,150), cv.FONT_HERSHEY_PLAIN,1.5,(0,255,0),2)
            
            pyautogui.moveTo(NewValueX,NewValueY)       #move mouse according to the converted values
            
          
        if m ==11:
            m=10        #if user press 's' again ,it will return to the last function
           
        
        
       
        if keyboard.is_pressed('d'): 
            m =0                                        #start over
        cv.imshow('frame',frame)
        u = 1                                           #show eyes windows if the program detects the face
                
                    
                   
       
                
        
    if u != 1:
        cv.imshow('frame',frame1)                   #show warning window if the program detects the face
        
        
    

     
    
    if cv.waitKey(1) == 13:     #if press 'enter' ,breaks the while loop
        break
    
cap.release()
cv.destroyAllWindows()      #release the capture and close all windows