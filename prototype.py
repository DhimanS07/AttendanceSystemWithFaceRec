import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf
from model import Model

class Prototype:
    def __init__(self,model_name):
        self.model_name = model_name # model name
        self.face_recognition = Model(dataset_dir=r'data')
        self.face_recognition.model = tf.keras.models.load_model(f'artifacts/{self.model_name}.h5')#load the model
        with open(f'artifacts\{self.model_name}_students.txt', 'r') as f:#load artifacts
            self.face_recognition.class_names = [line.strip() for line in f.readlines()]
        #open video capture
        self.video_capture = cv2.VideoCapture(0)
        #tkinter window
        self.window = tk.Tk()
        self.window.title("Real-Time Facial Recognition")
        self.window.geometry("800x600")
        #video feed label
        self.video_label = Label(self.window)
        self.video_label.pack()
        #text label to display the predicted name and confidence
        self.name_label = Label(self.window, text="Detected Student: None (Confidence: N/A)", font=("Arial", 16))
        self.name_label.pack()
        #exit button to close the application
        self.exit_button = Button(self.window, text="Exit", command=self.close_app, font=("Arial", 14), bg="red", fg="white")
        self.exit_button.pack(pady=10)
        #start video loop
        self.camera()
        #run tkinter mainloop
        self.window.protocol("WM_DELETE_WINDOW", self.close_app)
        self.window.mainloop()

    def camera(self):
        #capture video feed
        ret, frame = self.video_capture.read()
        if not ret:
            print("Failed to capture video")
            self.close_app()
            return
        # Perform face detection and prediction
        student_name, confidence = self.predict_image(frame)
        confidence_text = f"{confidence * 100:.2f}%" if confidence is not None else "N/A"
        self.name_label.config(text=f"Detected Student: {student_name} (Confidence: {confidence_text})")
        self.window.after(10, self.camera)  #call this method again after 10 ms
        
        #convert the frame to RGB (tkinter uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #convert the frame to an ImageTk format
        image = Image.fromarray(rgb_frame)
        image = ImageTk.PhotoImage(image)
        #update video label with the current frame
        self.video_label.config(image=image)
        self.video_label.image = image
        
    def predict_image(self, frame):        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #convert the frame to grayscale for face detection
        #use a pre-trained Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#draw a rectangle around the detected face            
            face_img = frame[y:y + h, x:x + w]  #crop the face from the frame
            #preprocess the face for prediction
            face_img = cv2.resize(face_img, (self.face_recognition.height, self.face_recognition.width))
            face_img = face_img / 255.0  #normalise
            face_img = np.expand_dims(face_img, axis=0)  #add batch dimension
            #predict the student name
            prediction = self.face_recognition.model.predict(face_img)
            predicted_class_idx = np.argmax(prediction[0])
            confidence = np.max(prediction[0])
            #return student name with confidence threshold
            if confidence > 0.8:  # Set a confidence threshold
                return self.face_recognition.class_names[predicted_class_idx], confidence
        return "Unknown", None

    def close_app(self):
        self.video_capture.release()
        self.window.destroy()

if __name__ == "__main__":
    model_name = input("Enter the model name: ") #prompt user for model name
    Prototype(model_name)