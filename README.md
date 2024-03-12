# accel-monitor-web-services
Accelerometer data storage and monitoring through Heroku PostgreSQL, RESTful, JSON and a Dash Web Application.

In this project, the values of all the acceleration axes of a robot simulated in CoppeliaSim are extracted and saved in a cloud database (Heroku Postgres). The developed system is depicted below:

![Accel_monitor_system](https://github.com/ro-afonso/accel-monitor-web-services/assets/93609933/400068a1-ae94-45d0-9e24-a9faa1e62dee)

The data is then displayed in a Dash Web Application, as shown below:

![Dash_Plotly_Accel_System](https://github.com/ro-afonso/accel-monitor-web-services/assets/93609933/40089c34-cb27-43fe-a822-9fc1bce19d00)

## Requirements
* Anaconda environment with Python 3.7: https://www.anaconda.com/products/individual
* CoppeliaSim Edu version 4.0.0: https://coppeliarobotics.com/files/CoppeliaSim_Edu_V4_0_0_Setup.exe
* VSCode or other code editors
* Heroku App using the 30 days free trial

## How to run
1) Change the Heroku app name to your app name in 'Hero.bat' and run the command
2) Install required packages:
   conda install -c anaconda git
   pip install -r requirements.txt
3) Initialize an empty git repo:
   git init
4) Initialize Heroku, add files and deploy:
   i) heroku login
   ii) heroku git:remote -a your-app-name # change the name for your app
   iii) git commit -am "initial commit"
   iv) git push heroku master # deploy the code to heroku
   v) heroku ps:scale web=1 # run with 1 heroku “dyno”
5) The app is now available at 'https://your-app-name.herokuapp.com'
6) Run the 'is_tp1_base.py' script to run the copelia sim and send the acceleration data to Heroku
7) Run the 'app.py' script and visit 'http://127.0.0.1:8050' in the web browser to display and monitor the data using Dash and Plotly
