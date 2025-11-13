# Aura IoT Home Assistant

## Distinctiveness and Complexity
Aura projet is a platform that allows users to add any iot device that can host a basic http server and allow Auras users to activate microcontrolers features and see data that microcontrolers could send back to Aura server.

Project is distrinct from other CS50W projects because it is a platform for storing, managing and utilizing microcontrolers for IoT purposes, therefore it should comply with distinctiveness requirement.

This project uses Django, has 6 models, heavily uses bootstrap, is mobile compatible, uses jacascript for async calls and dynamic UI updatingm, therefore it should comply with complexity requirement.

## Files and Their Purpose
### Purpose
Project is made up of 3 different applications:
- controlhub : Manages data, provides needed tools to control IoT hub (add devices, add actions for each device and either add http endpoints or assign Stat objects to each action).
- iotcore : Handles iot call logic. This app is not full done. I made it just to better outline what I want to do in the future. In this app, there will be custom http, MQTT protocol communication functions.
- auradash : Placeholder app that will handle dashboard functionality for IoT device network data. Currently I do not have any requirements of what data will be collected or how it needs to be vissualised, so this app is a placeholder for future development (made for planning purposes only).

### Files (cntrolhub)
#### **Commonn Django Project files**
Files I made no changes to that are part of the project will not be described here, if file is described bellow, this means there is custom code related to this project in that file. Files like: migrations, test.py, __init__.py, apps.py.
#### **admin.py**
Aura manages data through Django admin console page. This is primary and only way to manage date through UI. admin.py file registers models that need to be part of the admin console and customises some of the models for better experience.
#### **backend.py**
This is a custom backend for Users model that modifies how users authenticates. When creating a new user in Django, you need to use a username and an email, but when you register, you can only use your username, which was not ideal as some of my household guests, that will have access to some of my IoT devices, might not remember their username if they registered some time ago. New backend allows users to either log in by entering an email or username, this backend allows both without needing to specify which one you are using. It also prevents timing attackes, though this might not be that nescesary, as this IoT network is only meant to be working in an internal network.
#### **context_processor.py**
Decided to use global context manager as I added "active device" count value in each of the pages. This allows adding and managing this value in one spot, which keeping specific page contexts and render functions cleaner.
#### **models.py**
There are 6 models in models.py file in controlhub application. Bellow you can find each models description:

- *Device*: THis model stores information about IoT device. Any information that might be needed to identify what device it is, where its stored, its metadata like ip, mac, etc.

- *Connection*: Connection model handles relationships between MCUs. Some MCUs are not used a unit for controlling components (like: LEDs, sensors, heaters, relays, motors or anything that could be used to automate something in your home), but they are needed to transfer between various low wifi areas of the house/garden. Some MCUs will be of ESP32 type, which allows these microcontrollers to connect through ESP NOW procotocl and communicate with one another via radio waves. This allows us to build a chained MCU link that passes information like so AURA > MCU (withing WiFi range) > MCU (outside of Wifi Range). Connection stores information about connection between 2 MCUS and type of that MCU (either Node - just help communicate or Tail - controls components).

- *DeviceAction*: This model stores actions that MCU can do. Since MCUs usually have a lot of pins for controlling components, we can have many actions on a singular device. This model helps handle that type of information (http endpoints to call or in the future MQTT topics to subscribe to), action name for displaying in UI, etc.

- *User*: Django normally has User model already defined in default project/app, but I wanted to have custom field for my users that would allow to give user a more defined user type. Since plan is to allow my household guests use Aura, I want to define users who can add new information, who can access all of my houses IoT actions (for example my family members should be able to do everything, controll garden wattering level, check soil moisture levels, check composter internal temperature, controll automatic curtains) and who can only access guest actions (like check toilet vacancy status, change LED color that lights up my garden or toggle terrace heater or turn on tea pot by using Aura)

- *UserDeviceAccess*: This model controls what user sees what device. Access is controlled on device level, not action level. This might be changed in the future.

- *Stat*: This model stores sensor data. Each stat intance is a single measurement. Automatically gets a current date and time and JSON object with data that can be custom for each sensor.

#### **urls.py**
Common Django file, has nothing too unique, normal URLs for routing users in Aura application.

#### **views.py**
Common Django file, views.py handles all of the logic related to data management and main Aura UI rendering.

#### **style.css**
Common CSS styling file for handling style in HTML page.

#### **images (folder)**
Stores logo image files.

#### **active_devices.html (template)**
Active device summary page that shows all the active device activities through which you can quickly find active devices and turn them off if needebe.

#### **device_ctrl_page.html (template)**
Template that handle each devices action control page. Displays buttons and statisitics for sensors if there are any.

#### **index.html (template)**
Main page template. Displays all, for that user, accessible devices.

#### **layout.html (template)**
Main template that all pages uses. Has a header bar, burger menu for mobile.

#### **login.html (template)**
Handles logging in and redirecting to registration page.

#### **register.html (template)**
Handles registering in and redirecting to login page.

### Files (iotcore)
#### **urls.py**
Stores a single url endpoint for toggling a simulated device endpoint.

#### **views.py**
A single view that simulates MCU http request and return either a success (for when device managed to toggle) and failure for when device is not reachable due to poor bandwidth. Failure happens on a random basis, so ***if button blinks red after clicking it, this means random value that fails was selected and this behaviour is normal***.

#### **static/iotcore/script/calls.js**
Javascript file to do async http calls to a simulated http endpoint. This script also handles UI changes related with these API calls. Most vissual UI changes are related to updating data without needing to update page, also animated vissual indications for users to know what is happening.

## Running this application
To run Aura, you need to clone the project from the respository > create a pythons virtual environment > activate the venv > install django.

Project does not have any other dependencies.

First time you will need to run:
```python
python manage.py migrate
```

After you create the db file and migration files with previous command, you need to run the server
```python
python manage.py runserver
```

To do most of the work, you will need a superuser, so run this command and provide the required information in terminal window.
```python
python manage.py createsuperuser
```

After you create a super user account, you may access the Aura app and login.

After logging in, you need to click "Admin Console" button in the pages header. This will take you to admin console, where you can add devices (Device model), assign actions (DeviceAction model) to them. You will also need to enable devices that your account should be able to see (UserDeviceAccess model). Most fields can be filled out with fake/test information. All device actions with type "button" will perform the toggle http endpoint simulation. All actions with type: "sensor" will allow you to add Stat instances and assign them to a DeviceAction with type "sensor". If you are going to add Stat instances for a device, you will need to add data JSON object, whcih should be structured like so:

example data:
```json
{
    "temp., C": 15,
    "presure, bar": 4
}
```

This craetes a new data point entry with multiple data values. If in future, this device will return multiple sensor data, this can be used in a way presented above.

For "button" type of DeviceAction, you do not need to do any additional steps. Currently all buttons call the simulated http endpoint.

After you finish adding data for testing, you may return to site, and you should see bubbles with device names. Clicking on a bubble will take you to a device page, where you can interact or observe DeviceAction that you have created. Clicking a button will update UI with jacascript and call the endpoint asyncronously.

You can check sensor data for any DeviceAction that you created with type "sensor" and for which you hace added Stat instances. Each instance is a single line of data, so you need to add multiple to see more. In Device page sensor container you can see only last 10 data points.

## Additional comments
This project uses Python Django, templating, CSS, HTML, JavaScript (with async calls), is unique from other projects shown in this course. 

I really liked the course, found it easier to navigate than CS50 course, which I took a while ago. I know this project is not accepted as completed yet, just wanted to share my appretiation for the course team. Thank you.