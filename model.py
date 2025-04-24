import os
import random
import numpy as np
import tensorflow as tf
import cv2
from tensorflow import keras
from tensorflow.keras import layers 
from sklearn.model_selection import train_test_split

class Model:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir #directory containing student face images
        self.height = 128 #input image height 
        self.width = 128 #input image width
        self.input_shape = (self.height, self.width, 3) #input shape
        
        self.class_name = [] #to store the student involved in this class
        self.model = None #model
        self.cnn = None   #neural network model
    
    def student_img(self, min_images=1000):
        image_paths = [] #to store image paths
        labels = [] #to store labels
        student_count = {} #to store student image counts
        
        for idx, student in enumerate(os.listdir(self.dataset_dir)):
            student_path = os.path.join(self.dataset_dir, student)                       
            if not os.path.isdir(student_path):   #skip if not a directory
                continue
            student_images = []#collect image paths for this class
            for img in os.listdir(student_path):
                img_path = os.path.join(student_path, img)   #image path              
                if img.lower().endswith(('.png', '.jpg')):    #ensure it's an image file
                    student_images.append(img_path) #add image path to student_images
            if len(student_images) > min_images:
                student_images = random.sample(student_images, min_images) #randomly select 1000 images
            student_count[student] = len(student_images) #add student count
            self.class_name.append(student) #add student name involved in this class
            image_paths.extend(student_images) #add image paths
            labels.extend([idx] * len(student_images)) #add labels     
        #image count summary
        print("Student Image Counts:")
        for student, count in student_count.items():
            print(f"{student}: {count} images")
        
        X = [] #preprocess images
        for img_path in image_paths:
            img = cv2.imread(img_path)
            img = cv2.resize(img, (self.height, self.width)) #resize image
            img = img / 255.0  #normalise pixel values
            X.append(img) #add image to X        
        X = np.array(X) #convert to numpy array
        y = np.array(labels) #convert to numpy array    
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )#split data into training and validation set
        
        return X_train, X_val, y_train, y_val, len(self.class_name)
    
    def train(self, epochs=35, batch_size=128):
        X_train, X_val, y_train, y_val, students = self.student_img()    #load and preprocess data                
        self.cnn = CNN(input_shape=self.input_shape, students=students)   #initialise  CNN        
        #train the model
        model = self.cnn.train(X_train, y_train, X_val, y_val, epochs=epochs, batch_size=batch_size)         
        self.model = self.cnn.model #set the model for prediction
        return model
    
    def save_model(self, name='single'):
        if self.cnn is not None:            
            self.cnn.save_model(name)   #save model
            #save class names
            with open(f'artifacts/{name}_students.txt', 'w') as f:
                for class_name in self.class_name:
                    f.write(f"{class_name}\n")
    
    def predict(self, image_path):     
        #preprocess image
        img = cv2.imread(image_path)#read image
        img = cv2.resize(img, (self.height, self.width))#resize image
        img = img / 255.0  # normalize
        img = np.expand_dims(img, axis=0)  # add batch dimension        
        #make prediction
        predictions = self.model.predict(img)#predict image
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = self.class_name[predicted_class_idx]
        confidence = np.max(predictions[0])
        return {
            'student': predicted_class,
            'confidence': float(confidence)
        }   

    def summary(self): #model summary
        self.model.summary()

class CNN:
    def __init__(self, input_shape, students):
        self.input_shape = input_shape #input shape
        self.students = students #number of students
        #initialise model adam optimizer
        self.optimiser = tf.keras.optimizers.Adam()

        #build the CNN model
        self.model = self.model()
    
    #create model
    def model(self):
        model = keras.Sequential()       
        #convolutional layers
        model.add(layers.Conv2D(32, (3, 3), activation='relu',
                  input_shape=self.input_shape))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))        
        # flatten the output of the convolutional layers
        model.add(layers.Flatten())        
        # fully connected layers
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dropout(0.5))
        model.add(layers.Dense(self.students, activation='softmax'))               
        #compile the model
        model.compile(optimizer=self.optimiser,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                      metrics=['accuracy'])
        return model

    #train model
    def train(self, X_train, y_train, X_val, y_val, epochs, batch_size):
        model = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val)
        ) # epochs=35, batch_size=128
        return model
    
    #save model
    def save_model(self, name):
        os.makedirs('artifacts', exist_ok=True)
        save_path = os.path.abspath(f'artifacts/{name}.h5')
        self.model.save(save_path)

    
if __name__ == "__main__":
    #initialise recognition system
    face_recognition = Model(dataset_dir='data') #pathway to directories   
    model = face_recognition.train(epochs=35, batch_size=128) #train the model
    name_model = input("Enter model name: ") #name of the model
    face_recognition.save_model(name=name_model)    #save trained model  
    face_recognition.summary()  #model summary
    #prediction test
    result = face_recognition.predict(r'enter path location of an image you wish to test the model')
    print(f"Predicted Student: {result['student']}")
    print(f"Confidence: {result['confidence']:.2%}")