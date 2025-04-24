import cv2
import os
import numpy as np
import tensorflow as tf
import random
import time

#student name
STUDENT_NAME = input("input student name: ") 

# Ensures the data directory exists
def data_dir():
    #creates path for images
    data_path = os.path.join('data', STUDENT_NAME)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

def photos():
    #loading haarcascade classifier
    try:
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')        
        if faceCascade.empty():
            print("could not load face cascade classifier")
            return
    except Exception as e:
        print(f"Error: loading classifier: {e}")
        return

    #capturing real time video
    video_capture = cv2.VideoCapture(0)
    #check if video capture is opened successfully
    if not video_capture.isOpened():
        print("Error: webcam not found")
        return
    #captured images list
    captured_images = []
    last_time = 0
    try:
        while True:            
            ret, img = video_capture.read()     #reading image from webcam           
            if not ret:     #check if frame is read correctly
                print("Error: Can't receive frame")
                break     
            current_time = time.time() #get current time      
            #add text instructions on the image
            cv2.putText(img, f"Student: {STUDENT_NAME}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(img, "Press 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            coords, roi_img = detect(img, faceCascade)  #detect face 
            cv2.imshow("photo taking", img)            
            if len(coords) == 4 and roi_img is not None and (current_time-last_time) >=1.5:   #if face is detected         
                filename = save_img(roi_img)    #save dataset image               
                captured_images.append(roi_img) #store for potential augmentation
                print(f"Captured image: {filename}")
                last_time = current_time 
            if len(captured_images) >= 100: #break loop if 100 images are captured
                break        
            key = cv2.waitKey(1) & 0xFF #wait for key press
            if key == ord('q'): #break loop if 'q' is pressed
                print("exit successful")
                break            
        
        if captured_images:     #augmentation on captured images
            print("\nPerforming data augmentation on captured images...")
            for original_img in captured_images:
                original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)    #convert OpenCV BGR to RGB for TensorFlow
                augmented_images = data_aug(original_img_rgb)      #generate augmented images                
                for aug_img in augmented_images:    #save augmented images                    
                    aug_img_bgr = cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR)  #convert back to BGR for OpenCV saving
                    save_img(aug_img_bgr)            
            print(f"Generated {len(captured_images) * 10} augmented images. {len(captured_images)} original images saved.")

    finally:        
        video_capture.release() #releasing web-cam        
        cv2.destroyAllWindows() #self explanatory

def detect(img, faceCascade):   
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    #converts image to grey-scale
    # detecting features in grey-scale image and it returns coordinates, width and height of features
    faces = faceCascade.detectMultiScale(grey_img, 1.1, 10)    
    coords = [] #array to store coordinates of detected faces
    roi_img = None    #region of interest image
    for (x, y, w, h) in faces:
        #print(x, y, w, h) #print coordinates of detected face
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)  #draw rectangle around the face
        cv2.putText(img, "Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2) #label the face
        coords = [x, y, w, h]
        # if feature is detected, update region of interest by cropping image
        if len(coords) == 4:
            roi_img = img[y:y+h, x:x+w] # crop image to face region
            break  #take only the first detected face if multiple are found    
    return coords, roi_img #return coordinates and region of interest


def data_aug(img):    
    img = tf.cast(img, tf.float32)  #convert to uint8 to float32 (ensure proper shape)
    img = tf.image.resize_with_pad(img, 250, 250)  #resize image to 250x250 with padding    
    augmented_images = []   #store augmented images    
    for _ in range(10):
        seed1, seed2 = np.random.randint(0, 100000, size=2)        
        #augmentations on the images
        aug_img = tf.identity(img)
        aug_img = tf.image.stateless_random_brightness(aug_img, max_delta=0.2, seed=(seed1, seed2))#random brightness
        aug_img = tf.image.stateless_random_contrast(aug_img, lower=0.6, upper=1.4, seed=(seed1, seed2+1))#random contrast
        aug_img = tf.image.stateless_random_flip_left_right(aug_img, seed=(seed1, seed2+2))#random flip
        aug_img = tf.image.stateless_random_saturation(aug_img, lower=0.9, upper=1.1, seed=(seed1, seed2+3))#random saturation        
        #ensure pixel values are in valid range and convert back to uint8
        aug_img = tf.clip_by_value(aug_img, 0, 255)
        aug_img = tf.cast(aug_img, tf.uint8)        
        augmented_images.append(aug_img.numpy())    
    return augmented_images

#saving images
def save_img(img):    
    data_dir()  #ensure data directory exists before writing
    # generate unique filename with student name and random number
    filename = f"{STUDENT_NAME}_{random.randint(1,100000)}.jpg"
    file_path = os.path.join('data', STUDENT_NAME, filename)    
    cv2.imwrite(file_path, img) #write image 
    
    return filename

def SortUnknown(lfw, dest_dir):#function to sort unknown images
    files_moved = 0 
    for root, dirs, files in os.walk(lfw): #traverse through the directory
        for file in files: #tranverse through the files            
            current_path = os.path.join(root, file) #get current file path            
            new_path = os.path.join(dest_dir, file) #generate new file path
            os.replace(current_path, new_path) #move the file
            files_moved += 1 #increment files moved
            if files_moved >= 1000: #break loop if 1000 files are moved
                return

if __name__ == "__main__":
    photos()
    #SortUnknown('lfw', os.path.join('data', 'Unknown'))