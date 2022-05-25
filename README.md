# Django Smart Map Project

---
### Installation
1. Download PyCharm Professional Edition
2. Get educational license: https://www.jetbrains.com/community/education/#students
3. I recommend installing Miniconda as your Python interpreter: https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/index.html 
4. Clone this repository in PyCharm and create your own branch for development
5. Open a terminal in PyCharm and execute the following
   1. pip install django
   2. pip install python-socketio
6. (Optional) insert Google API key near bottom of django_transit/settings.py


### Run the Server
In a PyCharm terminal execute the following.
<li>python manage.py runserver

***

### Debugging
(The following images don't appear on GitHub, but they will in PyCharm)
<br><br>

#### Debug Python code
Click 'Add Configuration...' at top of PyCharm window.

![alt-text](readme-guide-images/Screen Shot 2022-05-16 at 11.01.11 AM.png "optional-title")

<br><br>
Click the "+" symbol at the top left. Select 'Python'.

![](readme-guide-images/Screen Shot 2022-05-17 at 11.23.07 AM.png)

<br><br>
Setup the configuration as shown. Set 'Script path' to your project's manage.py script.

![](readme-guide-images/Screen Shot 2022-05-17 at 10.57.29 AM.png)

<br><br>
Click in a file's gutter to add a breakpoint.

![](readme-guide-images/Screen Shot 2022-05-17 at 11.17.37 AM.png)

<br><br>
Click the green bug icon to run the server in debug mode. (You can use the green play button for regular mode.)

![](readme-guide-images/Screen Shot 2022-05-17 at 10.58.10 AM.png)

<br><br>
Click the server URL in the debug window output (or right-click it and select Chrome for javascript debugging).
![](readme-guide-images/Screen Shot 2022-05-19 at 12.46.30 PM.png)

<br><br>
Interact with the website to hit a breakpoint. Use the controls and tools in the debug window to step through the code and evaluate expressions.
![](readme-guide-images/Screen Shot 2022-05-19 at 1.05.05 PM.png)



#### Debug Javascript code
The easiest way right now is to open the server in Chrome. 
1. Similar to the Python debug steps, run the server but open the URL in Chrome. You can right-click on the URL and select Chrome.

2. Navigate to the Sources tab.
3. Click the file in the Page pane.
4. Set breakpoints by clicking in the file's gutter.
5. Step through the code using the buttons at the top of the righthand pane.
6. Evaluate expressions in the Console window at the bottom.
![](readme-guide-images/Screen Shot 2022-05-19 at 12.20.15 PM.png)

