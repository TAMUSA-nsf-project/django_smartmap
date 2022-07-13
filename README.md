# Django Smart Map Project

---

### Installation

1. Download PyCharm Professional Edition
2. Get educational license: https://www.jetbrains.com/community/education/#students
3. I recommend installing Miniconda to be your Python interpreter and virtual
   environment: [install Miniconda](https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/index.html)
4. Clone this repository in PyCharm and create your own branch for development
5. Open a terminal in PyCharm and execute the following
    1. pip install -r requirements.txt

If you have trouble with any of these steps, message me on discord.


***

### Running/Debugging

(The following images don't appear on GitHub, but they will in PyCharm)
<br><br>

#### Setup Run/Debug Configuration and Python Interpreter

In order for the location capture function to work properly, the application needs to be served over HTTPS. This is done
in the development environment by making use of the **sslserver** package in django.

Click 'Add Configuration...' at top of PyCharm window.

![alt-text](readme-guide-images/Screen Shot 2022-05-16 at 11.01.11 AM.png "optional-title")

<br><br>
Click the "+" symbol at the top left. Select 'Python'.

![](readme-guide-images/Screen Shot 2022-05-17 at 11.23.07 AM.png)

<br><br>
Setup the configuration as shown below. Set 'Script path' to your project's manage.py script.
<br><br>
**Note: Make sure to update the IP address in the parameters text box with your local IP address**. That is replace **<
192.168.1.154>** with your local IPV4 address. You can find the IPV4 address by executing the **ipconfig**
command in windows command prompt.
<ul>Python Interpreter: If you've installed Miniconda or Anaconda and haven't yet configured a 'Conda virtual environment' in your project, see the following instructions.</ul>

[Configure a Conda Virtual Environment](https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html)

![](readme-guide-images/Screen Shot 2022-05-17 at 10.57.29 AM.png)

Create a new environment variable named **ALLOWED_HOSTS_ENV** and assign it the value of your IPV4 address. This can be
done by executing the below command on your Windows machine command prompt or powershell as **Administrator**.

`setx ALLOWED_HOSTS_ENV "ADD_YOUR_IPV4_ADDRESS_HERE" /m`
<br><br>
Click in a file's gutter to add a breakpoint.

![](readme-guide-images/Screen Shot 2022-05-17 at 11.17.37 AM.png)

<br><br>
Click the green bug icon to run the server in debug mode. (You can use the green play button for regular mode.)

![](readme-guide-images/Screen Shot 2022-05-17 at 10.58.10 AM.png)

<br><br>
You may see something similar to the image shown below in your debug console. Click the URL after the text **_Starting
development server at_**
to access the application.
<ul>Note: If you are getting some error messages saying you need to add the IP to the allowed host list, please close and reopen the <b>pycharm</b>.
This is happening because the IDE is not able to read the newly created <b>ALLOWED_HOSTS_ENV</b> environment variable.</ul>

![](readme-guide-images/Screen Shot 2022-05-19 at 12.46.30 PM.png)

<br><br>
Interact with the website to hit a breakpoint. Use the controls and tools in the debug window to step through the code
and evaluate expressions.
![](readme-guide-images/Screen Shot 2022-05-19 at 1.05.05 PM.png)

#### Debug Javascript code

The easiest way right now is to open the server in Chrome.

1. Similar to the Python debug steps, run the server but open the URL in Chrome. You can right-click on the URL and
   select Chrome.

2. Navigate to the Sources tab.
3. Click the file in the Page pane.
4. Set breakpoints by clicking in the file's gutter.
5. Step through the code using the buttons at the top of the right-side pane.
6. Evaluate expressions in the Console window at the bottom.
   ![](readme-guide-images/Screen Shot 2022-05-19 at 12.20.15 PM.png)

### Simulating the Bus movement on the map for testing

This can be done using the android device emulator. There is some way to install the android device manager alone. But,
for now we need to install the android studio to get it working.

Follow the steps below.

1. Download and install the latest android studio from https://developer.android.com/studio#downloads.
2. Launch Android Studio.
3. Select the Virtual Device Manager Option<br><br>
   ![](readme-guide-images/android_studio_1.PNG)
   <br><br>
4. Click On create Device<br><br>
   ![](readme-guide-images/android_studio_2.PNG)<br><br>
5. Select an appropriate device as shown in the image below and click next.<br><br>
   ![](readme-guide-images/android_studio_3.PNG)<br><br>
6. Select a system image. Download if required. Click Next<br><br>
   ![](readme-guide-images/android_studio_4.PNG)<br><br>
7. Give an appropriate name and click Finish<br><br>
   ![](readme-guide-images/android_studio_5.PNG)<br><br>
8. Once the device is created, it will be available at the window we saw in step 3. Click on the Play button available
   next to the device that you created in the previous step to boot it up.<br><br>

   ![](readme-guide-images/android_studio_6.PNG)<br><br>

9. Once the device boots up, Click the 3 dots on the right bottom corner to open the settings.<br><br>
   ![](readme-guide-images/android_studio_7.PNG)<br><br>
10. Select Location option on the left side. Select the routes tab on the right side. Add a source and destination as we
    do it Google Maps. Click Save Route.<br><br>
    ![](readme-guide-images/android_studio_8.PNG)<br><br>
11. Select the route that you created in the previous step from the saved routes option and click the Play Route button
    on the right bottom corner. Make sure **Enable GPS Signal** toggle is ON.<br><br>
    ![](readme-guide-images/android_studio_9.PNG)<br><br>

12. Now go back to the android device screen and open our web app URL from the device. Navigate to the map tab and
    select a route. Now you can see the bus Moving on the map tab (In your browser window).<br><br>
    ![](readme-guide-images/android_studio_10.PNG)


