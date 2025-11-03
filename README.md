Noise-Controlled Task Manager 🎤🎧
A Python GUI application that automatically manages your focus by listening to your environment's noise level. If the ambient noise gets too high, it automatically enables Windows Focus Assist (Do Not Disturb) and pauses your media, helping you stay in the zone.

✨ Key Features
Live Noise Graph: A real-time Matplotlib graph visualizes the audio level from your microphone.

Automatic Focus Mode: When noise exceeds a custom threshold, the app automatically enables Windows Focus Assist.

Media Control: Simultaneously pauses your music or videos (Spotify, YouTube, etc.) by simulating the "Play/Pause" media key.

Adjustable Sensitivity: A simple slider lets you calibrate the perfect noise threshold for your environment.

Start/Stop Control: Manually control the monitoring at any time.

🛠️ How It Works
This tool is built with a few key Python libraries:

Tkinter: For the main application window, buttons, and slider.

Matplotlib: To embed and update the real-time noise graph.

Sounddevice & NumPy: To capture raw audio from the microphone and efficiently calculate its loudness (RMS).

Pynput: To simulate the media_play_pause key press.

Subprocess: To run PowerShell commands that directly control the Windows Focus Assist setting in the registry.

🚀 Getting Started
1. Prerequisites
Python 3.x

A working microphone

Windows 10 or 11 (see Platform Support below)

2. Installation
Clone this repository to your local machine:

Install the required Python libraries:

🖥️ How to Use
Run the main Python script:

Calibrate the Threshold (Important!)

Watch the graph while you are quiet. Note the "quiet" noise level.

Make some noise (talk, type, etc.). Note the "loud" noise level.

Move the "Noise Threshold" slider to a value between your quiet and loud levels. The red dashed line on the graph shows your selected threshold.

Press "Start" to begin monitoring.

When the noise level (blue line) crosses above the threshold (red line), Focus Mode will activate.

When it drops below the threshold, Focus Mode will deactivate.

Press "Stop" to disable monitoring. The app will automatically turn Focus Mode off if it was active.
