🎯 ProGamer Eye Trainer

An experimental eye-tracking training game built with Python, Pygame, and the EyeWare Beam SDK.
The game helps improve eye–hand coordination and reaction time by tracking gaze points and comparing them to a moving target on the screen.

📌 Features

✅ Uses the EyeWare Beam Eye Tracker SDK for real-time gaze tracking

✅ Fullscreen Pygame interface

✅ Calibration routine with multiple points to improve accuracy

✅ Always ensures gaze point stays visible on screen

✅ Simple reaction time training game (look at the target to "hit" it)

✅ Tracks and displays average reaction time + total hits

🖥 Requirements

Python 3.10+

EyeWare Beam SDK installed and running

A compatible eye tracker device

Libraries:

pip install pygame

🚀 How to Run

Clone this repository or download the script.

Ensure your EyeWare Beam service is running.

Run the game:

python eye_trainer_game.py


The game will start in fullscreen mode. Press ESC to exit.

🎮 Gameplay

Calibration Phase

The program shows red calibration dots at the corners of the screen.

Look directly at each dot.

The software collects gaze data and computes an offset correction.

Training Phase

A red circle (target) appears randomly on the screen.

Your gaze point (green dot) must reach the target.

When successful, a new target spawns, and your reaction time is recorded.

Stats

The top-left corner shows your average reaction time and the number of successful hits.

⌨ Controls

ESC → Exit the game

Mouse is disabled (only gaze is used for gameplay)

⚠ Troubleshooting

If you see Failed to start eye tracker, make sure:

The EyeWare Beam service is installed and running.

Your eye tracker is properly connected and supported.

If calibration fails, the game defaults to zero offset (less accuracy).

📖 License

This project is intended for educational and research purposes only.
All rights reserved © 2025.
