# How To Get Started

Here are instructions on how to collect training data and set up the AI models to generate the register list for the attendance system. It will outline the necessary libraries and provide step-by-step guidance on correctly preparing the training data and configuring the AI model. Additionally, it includes tips on creating an effective training dataset to ensure the AI model performs accurately and efficiently.

## 1. Gathering Training Data

This section prepares the training data so it can be used in `model.py` to create the AI model. You will begin with `photo.py`, which allows you to collect images of the individuals you want to add to the register list.

### 1.1 Libraries Needed To Be Downloaded
Here are the required libraries to run `photo.py`. You can install them by running the following command in the terminal:

`pip install [module_name]`

#### Required Libraries:

```python
import cv2
import os
import numpy as np
import tensorflow as tf
import random
import time
```
### 1.2 Running `photo.py`

When you run `photo.py`, you will be prompted to enter the name (preferably only write the first name with the initial of their second, example DhimanS) of the person, in the terminal, for whom you wish to capture images. This will create a folder with the entered name, which will be stored within the `data` folder. The images of the person will be saved in this folder.

The `data` folder already contains an `Unknown` folder, which holds images of random people from the **LFW database**. These images will be used to identify anyone who has not been trained in the model. Each person should have around 1000 images.

### 1.3 Capturing Optimal Images

Once the folder has been created, a window will pop up displaying the camera feed. The program will capture an image of the person once their face is detected, indicated by a rectangle around their face. Images will also be taken automatically every 1.5 seconds.  

To capture the most optimal images, the person should move slightly while facing the camera. Begin by facing directly forward for a few seconds, then slowly tilt the head up, followed by slow movements to the right and left. This will ensure that images are taken from different angles.  

Only 100 images will be captured initially, and the remaining images will be augmented to create 900 unique images. You can rerun the program to add more people.

## 2. Making The Model

This section of the you will make the model using `model.py`.

### 2.1 Libraries Needed To Be Downloaded

Here are the required libraries to run `model.py`. You can install them by running the following command in the terminal:

`pip install [module_name]`

#### Required Libraries:

```python
import os
import random
import numpy as np
import tensorflow as tf
import cv2
from tensorflow import keras
from tensorflow.keras import layers 
from sklearn.model_selection import train_test_split
```
### 2.2 Making The Model

Firstly, ensure that the `data` folder contains the individuals you want to include in the model. You can either delete the folders of unwanted individuals or move them to the `temporarily` folder.

Next, run the program, which will prompt you to input a name for the model in the terminal. The program will then generate the model file `model.h5` and the label file `model.txt`, both of which will be saved in the artifacts folder. The time it takes to create the model will depend on the number of people in the database.

In the following line:
```python
line 152 result = face_recognition.predict(r'enter here')
```
you can specify the location of one image from the database. This will be used to assess how well the model can identify a person.

### 2.3 Testing The Model with `prototype.py`

You can test the model by running `prototype.py`. First, you will need to input the name of the model you wish to test. A window will then pop up displaying the camera feed.

The person used to train the model should stand in front of the camera, and the program will attempt to predict their identity. The program will display the name of the person the model thinks it is, along with the confidence level.

## 3. Preparing `main.py`

There are a few things you will need to modify in `main.py` for all the components to work properly.

### 3.1 Libraries Needed To Be Downloaded

Here are the required libraries to run `main.py`. You can install them by running the following command in the terminal:

`pip install [module_name]`

#### Required Libraries:

```python
#for making the sql table
import sqlite3

# for the GUI
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, Entry, Toplevel,scrolledtext,colorchooser

#for face recognition
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageTk
from model import Model #no need to download this
import cv2
import threading

#attendace filing and other
import time
from datetime import datetime
import os
import numpy as np
import pandas as pd
import csv

#sending email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
```

### 3.2 Setting Up The Emailing System  

The emailing system will not work by default, as the account credentials have been removed. If you intend to use this system for real purposes, it is recommended to create either a burner account or a dedicated email account specifically for attendance-related tasks.  

#### Instructions:  
1. Go to [Google My Account](https://myaccount.google.com) and sign in with the account you wish to use for the emailing system.  
2. Search for and enable **2-Step Verification** (a phone number is required).  
3. Visit [Google App Passwords](https://myaccount.google.com/apppasswords) and log in again.  
4. Create an app password, set any name, and you will receive a 16-character password (do not share it with anyone).  
5. Copy the generated password and enter it into the following lines:  
   ```python
   line 754 PASSWORD = "enter app pass"  # from the send_mail method  
   line 797 PASSWORD = "enter app pass"  # from the mail_students method  
   ```  
6. Finally, add the email address in these lines:  
   ```python
   line 752 SENDER_EMAIL = "enter email here"  # from the send_mail method  
   line 796 SENDER_EMAIL = "enter email here"  # from the mail_students method  
   ```
7. You can change the message of the email from `mail_students` method by changing the content is `body` in **line 803** and **line 830**

### 3.3 Setting Up The `student.csv` File  

The final step is to add the email addresses for the individuals you have trained the model for.  

1. Open the `student.csv` file.  
2. In the first column, enter the names of the individuals. Ensure that each name matches exactly with the folder name used during training.  
3. In the second column, add the email address associated with each person.

### 3.4 How to Use the Rest of the Program

Once you run the programme, you will be greeted with the menu window. In the bottom-right corner, there is an **Info** button.  

Pressing the **Info** button will open a separate window that provides instructions on how to use the entire programme.  

You can find the **Info** button in the following sections: **Menu, Register, Login, and Settings**.
