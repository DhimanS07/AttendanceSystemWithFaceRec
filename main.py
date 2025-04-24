#for making the sql table
import sqlite3

# for the GUI
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, Entry, Toplevel,scrolledtext,colorchooser

#for face recognition
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageTk
from model import Model
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

def resetAttendanceFile(): #resets attendance file
    with open('attendance.csv','w') as f:
        f.truncate()
        heading = ["Student","Date","Time","Status","Class"]
        header = csv.DictWriter(f, delimiter=',',fieldnames=heading)
        header.writeheader()

def info():
    with open('info.txt','r') as f:
        with open("info.txt", "r") as file:
            support_message = file.read()
        
        #create a new window for the support message
        support_window = Toplevel()
        support_window.title("How It Works")
        support_window.geometry("500x400")

        #add a scrollable text widget
        text_area = scrolledtext.ScrolledText(support_window, wrap=tk.WORD, font=("Arial", 12))
        text_area.insert(tk.END, support_message)
        text_area.config(state="disabled")  #make the text widget read-only
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

class Accounts(): # class for databases holding account information
    def __init__(self):
        global conn, cursor # allows variables to be used throughout the code
        self._usern = "" # stores the user's username
        self._email = "" # stores the user's email
        self._pwd = "" # stores the user's password
        conn = sqlite3.connect("database.db") # establishes a connection to the database
        cursor = conn.cursor() # creates cursor to execute SQL queries
        self.database()

    def database(self): # creates tables needed to hold user’s information
        #cursor.execute("DROP TABLE IF EXISTS users")
        #cursor.execute("DROP TABLE IF EXISTS settings")

        #creates a table for the account information including username, email and password
        cursor.execute('''CREATE TABLE IF NOT EXISTS users(
            username VARCHAR(20) NOT NULL PRIMARY KEY,
            email VARCHAR(40) NOT NULL,
            password VARCHAR(15) NOT NULL)''')

        # ceates a table for all the settings of a person's account
        # the settings will be set to default upon creating an account
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings(
            username VARCHAR(20) NOT NULL PRIMARY KEY,
            font_size INT NOT NULL,
            dark BOOLEAN NOT NULL,
            background CHAR(7) NOT NULL,
            text CHAR(7) NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username));''')

        # pre making of an admin account -- the admin account will be used for testing
        cursor.execute("SELECT * FROM users WHERE username = 'admin' AND password = 'adminpass'")
        if cursor.fetchone() is None: # if no admin account exists, a new one is made in both tables
            cursor.execute("INSERT INTO users(username, email, password) VALUES('admin','admin@school2025.org','adminpass')")
            cursor.execute("INSERT INTO settings VALUES('admin', 14,'False', '#F0FFFF', '#0a0a0a')")

        conn.commit()

        # Displays all rows of both tables to confirm the data they hold
        # print(cursor.execute("SELECT * FROM users").fetchall())
        # print(cursor.execute("SELECT * FROM settings").fetchall())

    # get method to retrieve username stored in self._usern
    def get_usern(self):
        return self._usern

    #set method to change the username stored in self._usern
    def set_usern(self, usern):
        self._usern = usern

    # get method to retrieve email stored in self._email 
    def get_email(self):
        return self._email

    #set method to change the email stored in self._email
    def set_email(self, email):
        self._email = email

    # get method to retrieve password stored in self._pwd
    def get_pwd(self):
        return self._pwd

    #set method to change password stored in self._pwd
    def set_pwd(self, pwd):
        self._pwd = pwd

class Windows(tk.Tk):  # it creates Tkinter object/root window - inherits from Tk class
    def __init__(self):
        super().__init__()  # inherits methods from Tk class

        # style configuration for widgets
        self.style = ttk.Style(self)

        # default styling for the interface
        self.style.configure("TFrame", background="#F0FFFF")  #styling for frames
        self.style.configure("TLabel", foreground="#0a0a0a", background="#F0FFFF", font=("Lucida Console", 30))  #labels
        self.style.configure("TButton", foreground="#0a0a0a", font=("Arial", 18))  #buttons 

        # set title and window size
        self.title("ATTEND-INATOR")
        self.geometry("900x600")  # Defines window size
        self.minsize(900,600)# defines window with with minimun size of 900x600
        self.resizable(False,False)# disables window resizing

        #create a frame and assign it to self.container
        self.container = ttk.Frame(self, style="TFrame")
        self.container.grid(row=0, column=0, sticky="nsew")

        #configure layout to ensure proper alignment
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #creating dictionary to store frames for each screen
        self.frames = {}
        for F in (Menu, Register, Login, Control, Settings):  # frame classes
            frame = F(self.container, self)  #creates an instance of each frame class
            self.frames[F] = frame  # store each frame in the dictionary
            frame.grid(row=0, column=0, sticky="nsew")  #places frame onto root window
        #print(self.frames)
        self.show_frame(Menu)

    def StartFaceRec(self, model='test'): 
        frame = FaceRec(self.container,self,model) # creates an instance for Face recogntion window
        frame.grid(row=0,column=0, sticky='nsew')#places frame onto root window
        return

    def show_frame(self, container): 
        frame = self.frames[container]
        frame.tkraise()  #raise the frame to display it

        # Call the on_show method if it exists
        if hasattr(frame, "Username"):
            frame.Username()

    def styling(self):
        settings =cursor.execute(f"SELECT font_size, dark, background, text FROM settings WHERE username == '{accounts.get_usern()}'").fetchall()
        #print(settings)
        if settings[0][1]== 'True':
            self.style.configure("TFrame", background="#353935")
            #styling to change font, text and background colour of labels
            self.style.configure("TLabel", foreground="#353935", background="#EDEADE", font=("Lucida Console", 30))
            self.style.configure("Other.TLabel", foreground="#353935", background="#EDEADE", font=("Arial", int(settings[0][0])))
            # styling to change width, text and background colour of buttons
            self.style.configure("TButton", foreground="#353935", background="#EDEADE", font=("Arial", int(settings[0][0])))
        else:  
            self.style.configure("TFrame", background=f"{settings[0][2]}")
            #styling to change font, text and background colour of labels
            self.style.configure("TLabel", foreground=f"{settings[0][3]}", background=f"{settings[0][2]}", font=("Lucida Console", 20))
            self.style.configure("Other.TLabel", foreground=f"{settings[0][3]}", background=f"{settings[0][2]}", font=("Arial", int(settings[0][0])))
            # styling to change width, text and background colour of buttons
            self.style.configure("TButton", foreground=f"{settings[0][3]}", background=f"{settings[0][2]}", font=("Arial", int(settings[0][0])))
            # styling to change text and background colour of buttons
            self.style.configure("TEntry", foreground=f"{settings[0][3]}", font=("Arial", int(settings[0][0])))

class Menu(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__(container, style="TFrame")
        self.controller = controller

        #top frame for the title
        self.top = ttk.Frame(self, style="TFrame")
        self.top.grid(row=0, column=0, sticky="nsew")

        #form frame for buttons
        self.form = ttk.Frame(self, style="TFrame")
        self.form.grid(row=1, column=0, sticky="nsew")

        #configure row and column weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)  # extra row for anchoring the Info button south-east
        self.grid_columnconfigure(0, weight=1)

        # Title label
        self.lbl_title = ttk.Label(self.top, text="Menu", style="TLabel")
        self.lbl_title.pack(pady=20)

        # Buttons for Login and Register
        ttk.Button(self.form, text="Login", style="TButton", command=lambda: controller.show_frame(Login)).pack(pady=20)
        ttk.Button(self.form, text="Register", style="TButton", command=lambda: controller.show_frame(Register)).pack(pady=20)

        # Info button anchored to the bottom-right
        self.info = tk.Button(self, text="info", fg="white", bg="#838385", relief=tk.FLAT, width=8,height=2, command=info)
        self.info.grid(row=2, column=0, sticky="se", padx=10, pady=10)

class Register(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.email = tk.StringVar()  #to store the user's input in the email entry widget
        self.pwd = tk.StringVar()  #to store the user's input in the password entry widget
        self.key = tk.StringVar()  #to store the user's input in the confimation key entry widget

        # top frame for the title and back button
        self.top = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE, style="TFrame")
        self.top.pack(side=tk.TOP, fill=tk.X)

        #configure the grid for the top frame
        self.top.grid_columnconfigure(0, weight=1)  #back button column
        self.top.grid_columnconfigure(1, weight=1)  # title column
        self.top.grid_columnconfigure(2, weight=1)  #spacer column for balance

        #back button aligned to the left
        self.back = tk.Button(self.top, text="back", fg="white", bg="#838385", relief=tk.FLAT, width=5,
                                  command=lambda: self.goback())
        self.back.grid(row=0, column=0, sticky="w")

        #title
        self.lbl_title = ttk.Label(self.top, text="REGISTER", style="TLabel")# had to add spaces to align the title at the centre
        self.lbl_title.grid(row=0, column=1)

        # info button
        self.info = tk.Button(self.top, text="Info", fg="white", bg="#838385", relief=tk.FLAT, width=8,height=2, command=info)
        self.info.grid(row=0, column=2,sticky="e")

        #form frame is for placement of the entry widgets and corresponding labels
        self.form = ttk.Frame(self, style="TFrame")
        self.form.pack(side=tk.TOP, pady=(10, 10))

        # Widgets contained in the form frame:
        #email label and entry
        self.lbl_email = ttk.Label(self.form, text="Email:", style="Other.TLabel")
        self.lbl_email.grid(row=0, column=0, sticky="w",pady=20)
        self.ent_email = ttk.Entry(self.form, textvariable=self.email, font=("Arial", 10), width=25)
        self.ent_email.grid(row=0, column=1, pady=20, padx=20)

        #[assword label and entry
        self.lbl_password = ttk.Label(self.form, text="Password:", style="Other.TLabel")
        self.lbl_password.grid(row=1, column=0,sticky="w",pady=20)
        self.ent_password = ttk.Entry(self.form, textvariable=self.pwd, show="*", font=("Arial", 10), width=25)
        self.ent_password.grid(row=1, column=1, padx=20, pady=20)

        #key label and entry
        self.lbl_key = ttk.Label(self.form, text="Passkey:", style="Other.TLabel")
        self.lbl_key.grid(row=2, column=0, sticky="w",pady=20)
        self.ent_key = ttk.Entry(self.form, textvariable=self.key, show="*", font=("Arial", 10), width=25)
        self.ent_key.grid(row=2, column=1, padx=20, pady=20)

        # for placement of buttons
        self.bottom = ttk.Frame(self, style="TFrame")
        self.bottom.pack(side=tk.TOP, fill=tk.X)

        #register button
        self.btn_register = ttk.Button(self.bottom, text="Register", style="TButton", command=lambda: self.register())
        self.btn_register.pack(pady=30,padx=20)

    def register(self):
        if self.ent_email.get().strip() == "" or self.ent_password.get() == "" or self.ent_key.get() == "":#checks if entry are empty
            messagebox.showwarning("Warning","Please complete the required field")
            return

        if not self.check_email(self.ent_email.get()):#checking email format
            messagebox.showwarning("Warning", "Invalid email format. Please try again.")
            self.email.set("")
            return

        if self.email_exists(self.ent_email.get()):#checking if email exists already
            messagebox.showwarning("Warning", "Email already registered. Please use a different email.")
            self.email.set("")
            return

        if len(self.pwd.get()) < 8:#checking the length of the password
            messagebox.showwarning("Warning", "Password is too short, must be at least 8 characters.")
            self.pwd.set("")
            return

        if not any(c in ' !"#$%&\'()*+,/:;<=>?@[\\]^`{|}~' for c in self.pwd.get()):#password must have a special character
            messagebox.showwarning("Warning", "Password is weak, must have at least a special character.")
            self.pwd.set("")
            return

        if self.key.get() != "SCHOOL2025":#checking if they inputted the right confirmation code
            messagebox.showwarning("Warning", "Invalid confirmation key.")
            return

        #creating username
        username = self.create_username(self.email.get())  

        #allows the user to change the username
        user = messagebox.askyesno("Change Username", f"Your username is: {username}, Would you like to change your username?")
        if user:
            new_username = self.change_username()
            if new_username:  # Only update if a new username was provided
                username = new_username

        #fixed SQL queries with proper string formatting
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                    (username, self.email.get(), self.pwd.get()))
        cursor.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?)", 
                    (username, 14, True, '#F0FFFF', '#0a0a0a'))
        conn.commit()

        accounts.set_usern(username)
        accounts.set_email(self.email.get())
        accounts.set_pwd(self.pwd.get())

        messagebox.showinfo("Success", "Registration successful!")
        
        #clear inputs before switching frames
        self.email.set("")
        self.pwd.set("")
        self.key.set("")
        
        self.controller.show_frame(Login)

    def check_email(self, email: str) -> bool:
        if email.count("@") != 1:
            return False

        local, domain = email.split("@")
        #checks if local has special character or is empty--f=should be false
        if not local or any(c in ' !"#$%&\'()*+,/:;<=>?@[\\]^`{|}~' for c in local): 
            return False
        
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", 
                        "live.com", "icloud.com", "aol.com", "protonmail.com","isaacnewtonacademy.org","school2025.org"]

        if domain not in domains:
            return False

        for part in domain.split("."):
            if not part.isalnum() or not part:
                return False
        return True

    def email_exists(self, email:str)->bool:
        #searches for already existing email
        exist_email = cursor.execute(f"SELECT email FROM users WHERE email = '{self.email.get()}';").fetchall()
        if len(exist_email) !=0:
            return True
        return False

    #making unique username(by using emails)
    def create_username(self, email):
        base_username = email.split("@")[0]
        username = base_username
        count = 0
        while True:
            # First try without number
            if count == 0:
                username = base_username
            else:
                username = f"{base_username}{count}" 
            # Fixed the user existence check
            user = cursor.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
            if user is None:  # Username is available
                return username
            count += 1

    #change username
    def change_username(self):
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            new_username = simpledialog.askstring("Username", "Type new username:")
            if new_username is None:  #User clicked Cancel
                return None 
            if len(new_username) < 3:
                messagebox.showwarning("Warning", "Username must be at least 3 characters long.")
                attempts += 1
                continue 
            # Check if username exists
            user = cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,)).fetchone()
            if user is None:  # Username is available
                return new_username
            else:
                messagebox.showwarning("Warning", "Username taken, try again.")
                attempts += 1

    def goback(self):
        self.email.set("") #clears the email entry
        self.pwd.set("") #clears the password entry
        self.key.set("") #clears the confirmation key entry
        self.controller.show_frame(Menu)

class Login(ttk.Frame):
    def __init__(self, container, controller):
        
        super().__init__(container)
        self.controller = controller

        self.user = tk.StringVar()  # to store the user's input in the username/email entry widget
        self.pwd = tk.StringVar()  # to store the user's input in the password entry widget

        # top frame for the title and back button
        self.top = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE, style="TFrame")
        self.top.pack(side=tk.TOP, fill=tk.X)

        #configure the grid for the top frame
        self.top.grid_columnconfigure(0, weight=1)  #back button column
        self.top.grid_columnconfigure(1, weight=1)  #title column
        self.top.grid_columnconfigure(2, weight=1)  # spacer column for balance

        # back button
        self.back = tk.Button(self.top, text="back", fg="white", bg="#838385", relief=tk.FLAT, width=5,
                                  command=lambda: self.goback())
        self.back.grid(row=0, column=0, sticky="w")

        #title
        self.lbl_title = ttk.Label(self.top, text="LOGIN", style="TLabel")
        self.lbl_title.grid(row=0, column=1, sticky='')

        #info buttom
        self.info = tk.Button(self.top, text="Info", fg="white", bg="#838385", relief=tk.FLAT, width=8, height=2, command=info)
        self.info.grid(row=0, column=2,sticky="e")

        # form frame is for placement of the entry widgets and corresponding labels
        self.form = ttk.Frame(self, style="TFrame")
        self.form.pack(side=tk.TOP, pady=(10, 5))

        #widgets contained in the form frame:
        #user label and entry
        self.lbl_user = ttk.Label(self.form, text="User:", style="Other.TLabel")
        self.lbl_user.grid(row=0, column=0,sticky="w",pady=20)
        self.ent_user = ttk.Entry(self.form, textvariable=self.user, font=("Arial", 10), width=25)
        self.ent_user.grid(row=0, column=1, pady=5, padx=20)

        #password label and entry
        self.lbl_password = ttk.Label(self.form, text="Password:", style="Other.TLabel")
        self.lbl_password.grid(row=1, column=0,  sticky="w",pady=20)
        self.ent_password = ttk.Entry(self.form, textvariable=self.pwd, show="*", font=("Arial", 10), width=25)
        self.ent_password.grid(row=1, column=1, padx=20)

        #bottom frame is for placement of button
        self.bottom = ttk.Frame(self, style="TFrame")
        self.bottom.pack(side=tk.TOP, fill=tk.X)

        #log in button
        self.btn_login = ttk.Button(self.bottom, text="Log in", style="TButton", command=lambda: self.login())
        self.btn_login.pack(pady=20)

    def login(self):
        if self.user.get() =="" or self.pwd.get() =="":# check is the entry is empty
            messagebox.showwarning("Warning","Please complete the required field")
            return

        if len(self.pwd.get()) < 8:#check is password is short
            messagebox.showwarning("Warning", "Password is too short.")
            return   

        account_check = cursor.execute(f"SELECT username FROM users WHERE (username='{self.user.get()}' OR email='{self.user.get()}') AND password='{self.pwd.get()}';").fetchall()
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", 
                        "live.com", "icloud.com", "aol.com", "protonmail.com","isaacnewtonacademy.org","school2025.org"]
        if len(account_check) != 0:
            for i in domains:
                #if an account has been returned, then the account exists
                if i in self.user.get():#it checks if user has inputted their email instead of username
                    accounts.set_usern((account_check[0])[0]) #stores the username in attribute of the accounts class using set_usern() method
                else:
                    accounts.set_usern(self.user.get())  #stores the username in attribute of the accounts class using set_usern() method
            accounts.set_pwd(self.pwd.get())  #stores the password in attribute of the accounts class using set_pwd() method
            print(f"Username set in Accounts: {accounts.get_usern()}")
            print(f"Password set in Accounts: {accounts.get_pwd()}") 
            self.user.set("")  #clears the username entry  
            self.pwd.set("")
            self.controller.styling()  #styling is applied to the interface
            print("login")
            print(cursor.execute("SELECT * FROM settings").fetchall()) #prints the settings table
            self.controller.show_frame(Control)  #Control window is then displayed
        else:
            messagebox.showerror("Error", "This account does not exist. Please check your username/email or password.")
            # entry are sent to empty
            self.user.set("")
            self.pwd.set("")
    
    def goback(self):
        self.user.set("") #clears the email entry
        self.pwd.set("") #clears the password entry
        self.controller.show_frame(Menu)

class Control(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.classname = tk.StringVar()  #to store the selected class
        self.classes = [name.split('.h5')[0] for name in os.listdir('artifacts') if name.endswith('.h5')] #['13C', '13M', "images","test"]

        #top frame
        self.top = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE, height=100, style="TFrame")
        self.top.pack(side=tk.TOP, fill=tk.X)

        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=3)
        self.top.grid_columnconfigure(2, weight=1)

        #settings button
        self.back = tk.Button(self.top, text="⚙", fg="white", bg="#838385", relief=tk.FLAT, width=3,
                                  command=lambda: self.controller.show_frame(Settings))
        self.back.grid(row=0, column=2, sticky="e", padx=(0,3))

        #form frame
        self.form = ttk.Frame(self, height=200, width=500, style="TFrame")
        self.form.pack(side=tk.TOP, pady=20)

        self.attendance_report()# preparing for table for attendance report

        #dropdown label
        self.lbl_class = ttk.Label(self.form, text="Choose class:", style="Other.TLabel", font=("Arial", 15))
        self.lbl_class.grid(row=0, column=0, sticky="w", padx=(0,150))

        #dropdown menu
        self.class_dropdown = ttk.Combobox(
            self.form,
            textvariable=self.classname,
            values=self.classes,
            state="readonly",
            width=34
        )
        self.class_dropdown.grid(row=1, column=0, sticky="w", padx=(0,150))
        self.class_dropdown.set("Select a class")
        self.class_dropdown.bind("<<ComboboxSelected>>", lambda event: self.attendance_report()) #check is attandance.csv has IN/OUT, if not, then shows dummy or it updates to the list

        self.download = ttk.Button(self.form, text="download",style="TButton", command=lambda: self.download_file())
        self.download.grid(row=4, column=0,pady=10, columnspan= 2, padx=(0,150))

        #face Recognition Label
        self.lbl_facerec = ttk.Label(self.form, text="Face recognition", style="Other.TLabel", font=("Arial", 15))
        self.lbl_facerec.grid(row=0, column=2, sticky="n")

        #start registration Button
        self.btn_confirm = ttk.Button(self.form, text="Start Registration:",style="TButton", command=self.confirms_selection)# forgot style
        self.btn_confirm.grid(row=1, column=2, pady=10, columnspan=2, sticky="n")

        #body for email
        self.body = tk.Text(self.form, wrap=tk.WORD, height=14, width=30)
        self.body.insert("1.0", "Enter your message here...") #ghost message
        self.body.grid(row=2,column=2, sticky="n",columnspan=2, pady=5)
        self.body.bind('<FocusIn>', self.inbody)
        self.body.bind('<FocusOut>', self.outbody)

        #send email
        self.sendmail = ttk.Button(self.form, text="send mail", style="TButton", command=self.send_mail)
        self.sendmail.grid(row=4,column=2,columnspan=2, pady=10)

    def Username(self):
        username = accounts.get_usern()
        if username:
            #title with username
            self.lbl_title = ttk.Label(self.top, text=f"Welcome back, {username}!!! 🗿", style="TLabel")
            self.lbl_title.grid(row=0, column=0, sticky="w")
        else:
            #title without username
            self.lbl_title = ttk.Label(self.top, text="Welcome back!!! 🗿", style="TLabel")
            self.lbl_title.grid(row=0, column=0, sticky="w")
        return username
    
    def attendance_report(self, classname=None):
        try:
            # Clear any existing Treeview widgets
            for widget in self.form.winfo_children():
                if isinstance(widget, ttk.Treeview):
                    widget.destroy()

            #open the file and read content
            with open("attendance.csv", "r") as f:
                content = f.read()

            #check if the checks if any itemms under class is stored in the file
            if str(classname) in content:
                #preparing table
                tree = ttk.Treeview(
                    self.form,
                    columns=("Student", "Date", "Time", "Status", "Class"),
                    show="headings",
                )
                tree.grid(row=2, column=0, sticky="e", pady=5, columnspan=2, padx=(0,150))

                #set column headings and widths
                headers = ["Student", "Date", "Time", "Status", "Class"]
                for header in headers:
                    tree.heading(header, text=header)
                    tree.column(header, anchor="center", width=55)

                #enter itemms from csv file into table
                with open("attendance.csv", "r") as f:
                    reader = csv.DictReader(f)
                    reader.fieldnames = [field.strip() for field in reader.fieldnames]  #clean up header names
                    for row in reader:
                        tree.insert("","end",values=(row.get("Student", ""),row.get("Date", ""),row.get("Time", ""),row.get("Status", ""),row.get("Class", ""),),)
                # making the table editable
                def on_double_click(event):
                    item = tree.selection()[0]  #get selected item
                    column = tree.identify_column(event.x)  #get column clicked
                    if column != "#4":# user can only change itemms under status 
                        return
                    #print(column)
                    column_index = int(column.replace("#", "")) - 1  #convert column identifier to index
                    x, y, width, height = tree.bbox(item, column)  # bounding box of cell
                    value = tree.item(item, "values")[column_index]  # current value

                    #create entry widget for editing
                    entry = Entry(tree, width=width // 10)  #adjust width
                    entry.place(x=x, y=y + height // 2, anchor="center")
                    entry.insert(0, value)  #set initial value to be 0
                    
                    def save_edit(event=None):#save edits
                        new_value = entry.get()
                        values = list(tree.item(item, "values"))
                        values[column_index] = new_value
                        # tree.item(item, values=values)  # Update the Treeview
                        if new_value == "/" or new_value =="-":
                            try:#update the attendance.csv
                                tree.item(item, values=values)  # Update the Treeview
                                with open("attendance.csv","w", newline="") as f:
                                    writer = csv.DictWriter(f, fieldnames=headers)
                                    writer.writeheader()
                                    for row in tree.get_children():
                                        writer.writerow(dict(zip(headers, tree.item(row, "values"))))
                            except:
                                print("didn't work")
                            entry.destroy()
                        else:
                            messagebox.showwarning("Warning","Only enter '-' for absent or '/' for being present")
                            pass

                    entry.bind("<Return>", save_edit)  #save on enter key press
                    entry.focus_set()
                
                tree.bind("<Double-1>", on_double_click)  #bind double-click to edit
            else:
                self.dummy() #call for dummy report
        except FileNotFoundError:
            print("Error: attendance.csv file not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def dummy(self):# set up table with dummy report
        selected_class = self.classname.get()
        if selected_class not in self.classes:# this sets up an empty table with headings
            tree = ttk.Treeview(
                self.form,
                columns=("Student", "Date", "Time", "Status", "Class"),
                show="headings",
            )

            tree.grid(row=2, column=0, sticky="e", pady=5, columnspan=2, padx=(0,150))

            #set column headings and widths
            headers = ["Student", "Date", "Time", "Status", "Class"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, anchor="center", width=55) 
        else:
            #settings table with the name of student of chosen class and the heading
            tree = ttk.Treeview(
                self.form,
                columns=("Student", "Date", "Time", "Status", "Class"),
                show="headings",
            )
            tree.grid(row=2, column=0, sticky="e", pady=5, columnspan=2, padx=(0,150)) #added columnspan

            #set column headings and widths
            headers = ["Student", "Date", "Time", "Status", "Class"]
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, anchor="center", width=55)

            # load student name from the attendance report and insert in the table
            try:
                with open(f'artifacts\{selected_class}_students.txt', mode="r") as file:
                    for row in file:
                        if row.strip() != "Unknown":###bug fixed
                            tree.insert("", "end", values=(row.strip(), "", "", "", ""))
            except FileNotFoundError:
                messagebox.showerror("File Not Found", f"No attendance file found for class: {selected_class}")

    def confirms_selection(self):#confirms if class is selected before starting facial recogntion 
        selected_class = self.classname.get()
        if selected_class in self.classes:
            self.controller.StartFaceRec(selected_class)
        else:
            messagebox.showwarning("Selection Error", "Please select a valid class")
    
    def download_file(self):#downloading attendance report
        #open the file and read content
        with open("attendance.csv", "r") as f:
            content = f.read()

        #check if there is content under Status
        if ("/" in content) or ("-" in content):

            #get access to the user's Downloads folder
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            excel_file = os.path.join(downloads_folder, f"Attendance_{self.classname.get()}.xlsx")

            #read the CSV file using pandas
            df = pd.read_csv("attendance.csv")

            #save as Excel file to the downloads folder
            df.to_excel(excel_file, index=False)
            messagebox.showinfo("Success", f"Excel file saved successfully at {excel_file}") 

    def inbody(self,event):# deleting the placeholder text in the body text widget
        if self.body.get("1.0", tk.END).strip() == "Enter your message here...":
            self.body.delete("1.0", tk.END)
            self.body.config(fg='black') 

    def outbody(self, event):# displaying the placeholder text in the body text widget
        if self.body.get("1.0", tk.END).strip() == "":
            self.body.delete("1.0", tk.END)
            self.body.insert("1.0", "Enter your message here...")
            self.body.config(fg='gray')  

    def send_mail(self):
        #load the CSV files
        attendance = pd.read_csv('attendance.csv')
        students = pd.read_csv('student.csv')
        #filter students with status '-'
        absent = attendance[attendance['Status'] == '-']
        if len(absent) == 0:
            messagebox.showerror("Warning","There are no absent student")
            return
        print("2"+absent)
        #merge the attendance and student data on the student name to gather the email of student who are absent
        emails = pd.merge(absent, students, left_on='Student', right_on='student')['email']  
        print("1"+emails)

        #email configuration
        SENDER_EMAIL = "enter email here"
        RECIPIENT_EMAILS = emails.tolist()
        PASSWORD = "enter app password"  # App Password from Google
        SUBJECT = "Notices"
        body = self.body.get("1.0", tk.END).strip()  #get message from the text widget

        # check if the body is empty or has is the placeholder text -- if yes, show error
        if not body or body == "Enter your message here...":
            messagebox.showerror("Error", "Message cannot be empty!")
            return
        
        #create the email
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = ", ".join(RECIPIENT_EMAILS)
        message["Subject"] = SUBJECT
        message.attach(MIMEText(body, "plain"))
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  #start TLS encryption
                server.login(SENDER_EMAIL, PASSWORD)  #log in to Gmail
                server.send_message(message)  #send the email
                messagebox.showinfo("Success", "Email sent successfully.")                
                #clear the text widget and reset placeholder
                self.body.delete("1.0", tk.END)
                self.body.insert("1.0", "Enter your message here...")
                self.body.config(fg='gray')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

    def mail_students(self):
        #load the CSV files
        attendance = pd.read_csv('attendance.csv')
        students = pd.read_csv('student.csv')

        #filter students with status '-' and "/"
        absent = attendance[attendance['Status'] == '-']
        present = attendance[attendance['Status'] == '/']

        #merge the attendance and student data on the student name
        abs_mail = pd.merge(absent, students, left_on='Student', right_on='student')['email']
        psnt_mail = pd.merge(present, students, left_on='Student', right_on='student')['email']


        SENDER_EMAIL = "enter email here"
        PASSWORD = "enter app password"  # App Password from Google
        SUBJECT = "Notices"

        try:
            for email in abs_mail.tolist():#sends emails to students who are not in
                RECIPIENT_EMAILS = email
                body = f"""Dear Student,

Hope you doing well. You are marked absent for your {self.classname.get()} class. Please contant your teacher for learning. 

Best regards,
School

This is an automated message; please do not reply."""

                #create the email
                message = MIMEMultipart()
                message["From"] = SENDER_EMAIL
                message["To"] = RECIPIENT_EMAILS
                message["Subject"] = SUBJECT
                message.attach(MIMEText(body, "plain"))


                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()  #start TLS encryption
                    server.login(SENDER_EMAIL, PASSWORD)  #log in to Gmail
                    server.send_message(message)  #send the email
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        try:
            for email in psnt_mail.tolist():#sends emails to students who are in
                RECIPIENT_EMAILS = email
                body = f"""Dear Student,

You are marked in for your {self.classname.get()} class.

Best regards,
School

This is an automated message; please do not reply."""

                #create the email
                message = MIMEMultipart()
                message["From"] = SENDER_EMAIL
                message["To"] = RECIPIENT_EMAILS
                message["Subject"] = SUBJECT
                message.attach(MIMEText(body, "plain"))


                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()  #start TLS encryption
                    server.login(SENDER_EMAIL, PASSWORD)  #log in to Gmail
                    server.send_message(message)  #send the email   
        except Exception as e:
            print(f"Failed to send email: {e}")     

class FaceRec(ttk.Frame):
    def __init__(self, container, controller, model="test"):
        super().__init__(container)
        self.controller = controller

        #setting up the model
        self.model_name = model
        self.face_recognition = Model(dataset_dir=r'data')
        self.face_recognition.model = tf.keras.models.load_model(f'artifacts/{self.model_name}.h5')

        #loading labels
        with open(f'artifacts/{self.model_name}_students.txt', 'r') as f:
            self.face_recognition.class_names = [line.strip() for line in f.readlines()]

        self.last_prediction_time = time.time()#to track the time of the last prediction
        self.student_detected = {}  #to tracks consecutive detections
        self.attendance = {}  #to track attendance status

        #top Frame
        self.top = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE, height=100, style="TFrame")
        self.top.pack(side=tk.TOP, fill=tk.X)

        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=3)
        self.top.grid_columnconfigure(2, weight=1)

        #title
        self.lbl_title = ttk.Label(self.top, text="Facial Recognition", style="TLabel")
        self.lbl_title.grid(row=0, column=0, sticky="w")

        #leave button
        self.leave = tk.Button(self.top, text="Leave", fg="white", bg="#838385", relief=tk.FLAT, width=5, command=self.close)
        self.leave.grid(row=0, column=2, sticky="e", padx=4)

        #form Frame
        self.form = ttk.Frame(self, height=200, width=500, style="TFrame")
        self.form.pack(side=tk.TOP, pady=20)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Detect available cameras dynamically
        self.cam_list = []
        i = 0
        while True:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cam_list.append(i)
                cap.release()
            else:
                break  # Stop when no more valid cameras are found
            i += 1

        if len(self.cam_list) == 0:
            self.text.config(text="Failed to capture video.")
            messagebox.showerror("Error","Camera not found, please check connections")
            #call the attendance_report method to uptable the table first
            self.controller.show_frame(Control) 

        # Create a dropdown menu for camera selection
        self.cam_var = tk.StringVar(value=self.cam_list[0] if self.cam_list else "No Camera")
        self.camera_optn = ttk.Combobox(self.top, textvariable=self.cam_var, values=self.cam_list, state="readonly")
        self.camera_optn.grid(row=0,column=1, sticky="", padx=(0,190))
        self.camera_optn.bind("<<ComboboxSelected>>", self.switch_cams)

        # Initialize video capture with the first camera
        if self.cam_list:
            self.cap = cv2.VideoCapture(self.cam_list[0])
        else:
            self.cap = None  # No available cameras

        #video feed
        self.video_label = ttk.Label(self.form)
        self.video_label.grid(row=0, column=0, sticky="")

        self.text = ttk.Label(self.form, text="Detecting faces", style="TLabel", font= 12)
        self.text.grid(row=1, column=0, sticky="ns")

        self.update_video()

    def update_video(self):
        #capture the video frame
        ret, frame = self.cap.read()
        if not ret:
            return  

        #convert the frame to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #convert frame to ImageTk format
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(rgb))

        #update the video label
        self.video_label.config(image=img_tk)
        self.video_label.image = img_tk

        #perform face detection in a separate thread
        current_time = time.time()
        if current_time - self.last_prediction_time >= 2:
            threading.Thread(target=self.process_face, args=(rgb,)).start()
            self.last_prediction_time = current_time

        #schedule the next frame update
        self.after(10, self.update_video)

    def process_face(self, frame):
        self.mark_attendance("filler") #marking student out
        student_name, confidence = self.detect_face(frame)
        confidence_text = f"{confidence * 100:.2f}%" if confidence else "N/A"
        # self.text.config(text=f"Detected Student: {student_name} (Confidence: {confidence_text})") #checking the confidence
        self.text.config(text=f"You must be... {student_name}, confidence: {confidence_text}", font=12)
        self.mark_attendance(student_name)#save in attendance report
        print(self.attendance)

    def detect_face(self, frame):
        # convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #use a pre-trained Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            #draw a rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            #crop the face from the frame
            face_img = frame[y:y + h, x:x + w]

            #preprocess the face for prediction
            face_img = cv2.resize(face_img, (self.face_recognition.height, self.face_recognition.width))
            face_img = face_img / 255.0  #normalise
            face_img = np.expand_dims(face_img, axis=0)  #add batch dimension

            #predict the student name
            prediction = self.face_recognition.model.predict(face_img)
            predicted_class_idx = np.argmax(prediction[0])
            confidence = np.max(prediction[0])

            #return student name with confidence threshold
            if confidence > 0.8:#confidence threshold at 80%
                return self.face_recognition.class_names[predicted_class_idx], confidence

        return "Unknown", None

    def mark_attendance(self, student_name):
        #mark all other students as "-" if not currently detected
        if not self.attendance:
            for student in self.face_recognition.class_names:
                if "Unknown" == student or student == "filler":
                    pass #continue
                else:
                    self.attendance[student] = "-"
        
        if student_name == "Unknown" or student_name == "filler":#if student is unknown
            return
        
        #count consecutive detections need to be taken before updating the status
        self.student_detected[student_name] = self.student_detected.get(student_name, 0) + 1
        #print(self.student_detected)
                
        if self.student_detected[student_name] >= 3:
            self.attendance[student_name] = "/"

        if all(status == "/" for status in self.attendance.values()):
            self.leave.invoke() #close the window

    def save_attendance(self):
        classname = self.model_name
        date_today = datetime.now().strftime("%x")#storing the date of registration
        time_today = datetime.now().strftime("%X")#storing the time of registration
        attendance_data = [
            {"Student": name, "Date": date_today, "Time": time_today, "Status": status, "Class": classname}
            for name, status in self.attendance.items()
        ]

        #sort attendance name alphabetically
        attendance_data.sort(key=lambda x: x["Student"])

        #save it in the attendance csv file
        with open("attendance.csv", mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Student", "Date", "Time", "Status", "Class"])
            writer.writeheader()
            writer.writerows(attendance_data)
    
    def switch_cams(self, event=None):
        selected_camera = int(self.cam_var.get())  # Get the selected camera index

        # Ensure the old camera is properly released
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        # Open the new camera
        new_cap = cv2.VideoCapture(selected_camera)
        if not new_cap.isOpened():
            self.text.config(text="Failed to switch camera!")
            return

        # Assign the new camera and restart video feed
        self.cap = new_cap
        self.text.config(text=f"Switched to Camera {selected_camera}")

            
    def close(self):
        self.save_attendance()  #save attendance before destroying the window
        self.cap.release() # release access of camera
        #call the attendance_report method to uptable the table first
        control_frame = self.controller.frames[Control]
        control_frame.attendance_report(self.model_name) 
        #email the students
        control_frame.mail_students()
        #switch to Control window
        self.controller.show_frame(Control)               

class Settings(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__(container)
        self.controller = controller
        self.font = tk.StringVar()  #stores input from font entry widget
        self.dark = tk.IntVar()     #stores value of dark check button (0/1 = off/on)

        #configure grid for the main frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        #top frame
        self.top = ttk.Frame(self, borderwidth=2, relief=tk.GROOVE, height=100, style="TFrame")
        self.top.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        #configure grid in the top frame
        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=3)
        self.top.grid_columnconfigure(2, weight=1)

        #back button
        self.back = tk.Button(self.top, text="<", fg="white", bg="#838385", relief=tk.FLAT, width=5,
                              command=lambda: self.controller.show_frame(Control))
        self.back.grid(row=0, column=0, sticky="w", padx=4)

        #title
        self.lbl_title = ttk.Label(self.top, text="SETTINGS", style="TLabel")
        self.lbl_title.grid(row=0, column=1, sticky="")

        #log out button
        self.logout = tk.Button(self.top, text="Log Out", fg="white", bg="#838385", relief=tk.FLAT, width=5,
                                command=self.log_out) 
        self.logout.grid(row=0, column=2, sticky="e", padx=(0, 5))

        #form frame
        self.form = ttk.Frame(self, height=200, width=500, style="TFrame")
        self.form.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        #configure grid for central alignment in the form frame
        self.form.grid_columnconfigure(0, weight=1)
        self.form.grid_columnconfigure(1, weight=1)

        #font label
        self.lbl_font = ttk.Label(self.form, text="Font:", style="Other.TLabel", font=("Arial", 14))
        self.lbl_font.grid(row=0, column=0, padx=(0,150), pady=(25,15), sticky="e")

        #font spinbox
        self.spin_font = tk.Spinbox(self.form, from_=14, to=24, fg="#091C4F", font=14, textvariable=self.font, width=10)
        self.spin_font.grid(row=0, column=1, pady=(25,15), sticky="w")

        #dark mode label
        self.lbl_dark = ttk.Label(self.form, text="Dark Mode:", style="Other.TLabel", font=("Arial", 14))
        self.lbl_dark.grid(row=1, column=0,padx=(0,98), pady=15, sticky="e")

        #dark mode check button
        self.check_dark = tk.Checkbutton(self.form, variable=self.dark, bg="#FFBF00", fg="#091C4F",command=self.save)
        self.check_dark.grid(row=1, column=1, sticky="w", padx=(50,0), pady=15)

        #background colour button
        self.bg = ttk.Button(self.form, text="Background", style="TButton", width=14, 
                                 command=lambda: self.colour("background"))
        self.bg.grid(row=2, column=0, pady=25, padx=(0,50), sticky="e")

        # Text colour button
        self.text = ttk.Button(self.form, text="Text", style="TButton", width=14, command=lambda: self.colour("text"))
        self.text.grid(row=2, column=1, pady=25, sticky="w")

        #save changes button
        self.btn_save = ttk.Button(self.form, text="Save Changes", style="TButton", width=14, command=self.save)
        self.btn_save.grid(row=3, column=0, pady=25,padx=(0,50), sticky="e")

        #reset button
        self.btn_reset = ttk.Button(self.form, text="Reset to default", style="TButton", width=14, command=self.reset)
        self.btn_reset.grid(row=3, column=1, pady=25, sticky="w")

        #info button 
        self.info = tk.Button(self, text="Info", fg="white", bg="#838385", relief=tk.FLAT, width=8,height=2, command=info)
        self.info.grid(row=3, column=0, sticky="se", padx=20, pady=20)

    def save(self):
        if self.font.get() == "":# check if the spinbox is empty
            messagebox.showwarning("Warning","input font size")
        else:
            try:
                #checks if the integer entered is within the spinbox range
                if int(self.font.get()) >= 14 and int(self.font.get()) <= 22:
                    #if within the range, the database is updated with the new font size
                    cursor.execute(f"UPDATE settings SET font_size = '{self.font.get()}' WHERE username = '{accounts.get_usern()}'")
                else:
                    #error message is displayed
                    messagebox.showwarning("Warning","Font size out of range: 14-22")
            except:
                #if the wrong data type is entered an error message will be displayed
                messagebox.showwarning("Warning","Font size must be an interger")
        
        #print(self.dark.get())

        if self.dark.get() == 1:#gets value of checkbutton - if == 1, the button has been selected
            #dark has been selected so user's settings are updated and dark is set to true
            cursor.execute(f"UPDATE settings SET dark = 'True' WHERE username = '{accounts.get_usern()}'")
        else:
            cursor.execute(f"UPDATE settings SET dark = 'False' WHERE username = '{accounts.get_usern()}'")   
        conn.commit()#saves the changes to the database
        
        #print(cursor.execute("SELECT * FROM settings").fetchall())
        self.controller.styling()  # calls the styling function to update the GUI
    
    def reset(self):
        cursor.execute(f"UPDATE settings SET font_size= '14', dark= 'False',background= '#F0FFFF', text= '#0a0a0a' WHERE username = '{accounts.get_usern()}'")
        conn.commit()#the change to the database is saved
        self.controller.styling()

    def colour(self,hex):
        colour_code = tk.colorchooser.askcolor(title =f"Choose {hex} colour") #displays the colour picker and stores the hex code
        #uses the passed in feature, hex code and stored username to change the colour code in settings for the user
        cursor.execute(f"UPDATE settings SET '{hex}' = '{colour_code[1]}' WHERE username = '{accounts.get_usern()}'")
        conn.commit()#the change to the database is saved
        #print(cursor.execute("SELECT * FROM settings").fetchall())

    def log_out(self):
        #clear stored user information
        accounts.set_usern("")
        accounts.set_email("")
        accounts.set_pwd("")
        
        #destroys the entire application window and recreate it
        #this is the most comprehensive way to reset all styling
        self.controller.destroy()
        resetAttendanceFile()
        
        #create a new application instance
        app = Windows()
        app.mainloop()
        return  #exit this method as the application has been restarted

if __name__ == "__main__":
    resetAttendanceFile()
    accounts = Accounts()
    screen = Windows()
    screen.mainloop()