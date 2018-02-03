ReminderBot project

This project contains python3 script files for a reminder telegram bot, whos aim is to save and remind notes for users.

Baisicaly it contains four *.py files. The ReminderBot.py file contains the main bot code with GUI, made on PyQt5.
Other three files contains some specified functions for bot to work (HTTP transfer functions, SQL query functions, regular expression check functions).
Also the project contains a venv directiory with virtual environment for project to run and a pycache directory with caches.

For project to work properly you need to add next information to a file bot.info in project directory.
First line should contain telegram bot token.
Second line should contain update number (at start it can be -102 to get all updates and culculate real update number).

Python 3.5 project.
Used packages:
PyQt5	V5.9.2
pip	V9.0.1
setuptools 	V38.4.0
sip	V4.19.6
wheel	V0.30.0 

Brunman Mikhail -Taimish- (c) 2018
