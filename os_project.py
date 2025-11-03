# Noise-Controlled Task Manager

import sounddevice as sd
import numpy as np
import subprocess
import time
from pynput.keyboard import Key, Controller
import tkinter as tk
from tkinter import ttk
from collections import deque

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DEFAULT_NOISE_THRESHOLD = 0.02  # How loud before we take action
SAMPLE_RATE = 44100  # Audio quality
CHUNK_SIZE = 1024  # Audio processing size
COOLDOWN_PERIOD = 3  # Seconds to wait between actions
PLOT_POINTS = 100  # Number of data points to show on graph

current_noise_level = 0
noise_data = deque([0] * PLOT_POINTS, maxlen=PLOT_POINTS)
keyboard = Controller()
stream = None
update_loop_id = None
focus_mode_active = False
last_action_time = 0


def audio_callback(indata, frames, time_info, status):
    
    global current_noise_level
    
    if status:
        print(f"Audio status: {status}")
    
    # Calculate the volume level (RMS = Root Mean Square)
    volume = np.linalg.norm(indata) * 10
    current_noise_level = volume / len(indata)
    
    # Add the new noise level to our history for the graph
    noise_data.append(current_noise_level)


def pause_media():
    keyboard.press(Key.media_play_pause)
    keyboard.release(Key.media_play_pause)
    print("Media paused")


def toggle_focus_mode(enable):
    
    print(f"{'Enabling' if enable else 'Disabling'} focus mode...")
    
    # Registry value: 1 = On, 0 = Off
    setting = '1' if enable else '0'
    
    # PowerShell command to modify Windows registry
    command = (
        f'powershell.exe -ExecutionPolicy Bypass -Command "'
        f'if (!(Test-Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings\')) {{ '
        f'New-Item -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\' -Name \'Settings\' -Force; '
        f'}}; '
        f'Set-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings\' '
        f'-Name \'FocusAssist\' -Value {setting}"'
    )
    
    subprocess.run(command, check=True, shell=True, 
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Focus mode {'enabled' if enable else 'disabled'} successfully")


def update_everything():
    
    global update_loop_id, focus_mode_active, last_action_time
    
    threshold = DEFAULT_NOISE_THRESHOLD
    
    noise_label_var.set(f"Current Noise: {current_noise_level:.4f}")
    
    time_since_last_action = time.time() - last_action_time
    
    # If noise is HIGH and focus mode is OFF
    if current_noise_level > threshold and not focus_mode_active:
        if time_since_last_action > COOLDOWN_PERIOD:
            print("\nHigh noise detected!")
            toggle_focus_mode(True)
            pause_media()
            focus_mode_active = True
            last_action_time = time.time()
            status_var.set("Status: Focus Mode ON 🔒")
    
    # If noise is LOW and focus mode is ON
    elif current_noise_level < threshold and focus_mode_active:
        if time_since_last_action > COOLDOWN_PERIOD:
            print("\nNoise level back to normal")
            toggle_focus_mode(False)
            focus_mode_active = False
            last_action_time = time.time()
            status_var.set("Status: Listening... 🎤")
    
    # Update the graph
    ax.clear()
    ax.plot(noise_data, color='blue', linewidth=2)
    
    # Draw the threshold line
    ax.axhline(y=threshold, color='red', linestyle='--', 
               linewidth=2, label=f'Threshold: {threshold:.2f}')
    
    # Make the graph look nice
    ax.set_ylim(0, max(0.2, max(noise_data) * 1.2))
    ax.set_xlim(0, PLOT_POINTS)
    ax.set_ylabel("Noise Level")
    ax.set_xlabel("Time")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    canvas.draw()
    
    update_loop_id = root.after(100, update_everything)


def start_button_clicked():
    global stream, last_action_time
    
    if stream and stream.active:
        print("Already running!")
        return
    
    last_action_time = 0
    status_var.set("Status: Starting...")
    
    # Start listening to microphone
    stream = sd.InputStream(
        callback=audio_callback,
        channels=1,
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE
    )
    stream.start()
    
    status_var.set("Status: Listening... 🎤")
    
    # Update button states
    btn_start.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)
    
    # Start the update loop
    update_everything()


def stop_button_clicked():
    global update_loop_id, focus_mode_active, stream
    
    # Stop the update loop
    if update_loop_id:
        root.after_cancel(update_loop_id)
        update_loop_id = None
    
    # Stop listening to microphone
    if stream:
        stream.stop()
        stream.close()
        stream = None
    
    # Turn off focus mode if it's on
    if focus_mode_active:
        toggle_focus_mode(False)
        focus_mode_active = False
    
    status_var.set("Status: Stopped")
    noise_label_var.set("Current Noise: --")
    
    # Update button states
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)


def on_window_close():
    print("Closing application...")
    stop_button_clicked()
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("Noise-Controlled Task Manager")
root.geometry("650x650")

# Variables for GUI elements
noise_label_var = tk.StringVar(value="Current Noise: --")
status_var = tk.StringVar(value="Status: Stopped")

# Create the graph
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Real-Time Noise Level Monitor")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=10, pady=10)

# Create control panel at bottom
control_frame = ttk.Frame(root, padding="10")
control_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Status label
lbl_status = ttk.Label(control_frame, textvariable=status_var, 
                       font=("Arial", 12, "bold"))
lbl_status.pack(pady=5)

# Current noise level label
lbl_noise = ttk.Label(control_frame, textvariable=noise_label_var, 
                      font=("Arial", 10))
lbl_noise.pack(pady=5)

# Threshold display (fixed value, not adjustable)
lbl_threshold = ttk.Label(control_frame, 
                         text=f"Noise Threshold: {DEFAULT_NOISE_THRESHOLD:.3f}",
                         font=("Arial", 10))
lbl_threshold.pack(pady=10)

# Buttons
btn_frame = ttk.Frame(control_frame)
btn_frame.pack(pady=15, fill=tk.X)

btn_start = ttk.Button(btn_frame, text="▶ Start Monitoring", 
                       command=start_button_clicked)
btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 10))

btn_stop = ttk.Button(btn_frame, text="⏹ Stop Monitoring", 
                      command=stop_button_clicked, state=tk.DISABLED)
btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 20))

# Handle window close
root.protocol("WM_DELETE_WINDOW", on_window_close)

# Instructions label
instructions = ttk.Label(
    control_frame,
    text="Click Start to begin monitoring. App will pause media when noise exceeds threshold.",
    font=("Arial", 8),
    foreground="gray"
)
instructions.pack(pady=(10, 5))

# Start the application
print("Noise-Controlled Task Manager Started")
print("Click Start to begin monitoring")
root.mainloop()