import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt
import shelve
from twilio.rest import Client

# MQTT settings
broker_address = "mqtt-dashboard.com"
port = 1883
smoke_topic = "smoke/data"

# Twilio settings
account_sid = "your_account_sid"
auth_token = "your_auth_token"
twilio_client = Client(account_sid, auth_token)
from_phone = "your_twilio_phone_number"
to_phone = "your_phone_number"

# Function to handle MQTT connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(smoke_topic)
    else:
        print(f"Failed to connect, return code {rc}")

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    data = msg.payload.decode()
    if msg.topic == smoke_topic:
        update_smoke(data)

# Function to make a call
def make_call(smoke_level):
    message = f"Alert! The smoke level is {smoke_level} PPM, which exceeds the safe limit."
    call = twilio_client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        to=to_phone,
        from_=from_phone
    )
    print(f"Call initiated with SID: {call.sid}")

# Function to update Smoke label
def update_smoke(data):
    smoke_level = int(data)
    smoke_label.config(text=f"Smoke Level: {smoke_level} PPM")
    if smoke_level > 400:
        make_call(smoke_level)

# Function to sign up a new user
def sign_up():
    username = entry_username.get()
    password = entry_password.get()
    with shelve.open('credentials') as db:
        if username in db:
            messagebox.showerror("Error", "Username already exists!")
        else:
            db[username] = password
            messagebox.showinfo("Success", "Sign up successful! You can now log in.")

# Function to log in an existing user
def log_in():
    username = entry_username.get()
    password = entry_password.get()
    with shelve.open('credentials') as db:
        if username in db and db[username] == password:
            messagebox.showinfo("Success", "Login successful!")
            login_frame.pack_forget()
            show_monitor()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

# Function to show the monitoring window
def show_monitor():
    global smoke_label
    monitor_frame = tk.Frame(root)
    monitor_frame.pack(pady=20)

    smoke_label = ttk.Label(monitor_frame, text="Smoke Level room 1: ", font=("Helvetica", 16))
    smoke_label.pack(pady=10)
    smoke_label2 = ttk.Label(monitor_frame, text="Smoke Level room 2: ", font=("Helvetica", 16))
    smoke_label2.pack(pady=10)
    exit_button = ttk.Button(monitor_frame, text="Exit", command=root.quit)
    exit_button.pack(pady=10)

    client.connect(broker_address, port)
    client.loop_start()

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Create the main window
root = tk.Tk()
root.title("Smoke Level Monitor")

# Create the login frame
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

ttk.Label(login_frame, text="Username:").pack(pady=5)
entry_username = ttk.Entry(login_frame)
entry_username.pack(pady=5)

ttk.Label(login_frame, text="Password:").pack(pady=5)
entry_password = ttk.Entry(login_frame, show="*")
entry_password.pack(pady=5)

signup_button = ttk.Button(login_frame, text="Sign Up", command=sign_up)
signup_button.pack(pady=5)

login_button = ttk.Button(login_frame, text="Log In", command=log_in)
login_button.pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
