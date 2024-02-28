from distutils.util import execute
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_caching import Cache
import sim
import time 
import threading
#import requests
import psycopg2
import os
from random import randrange

app = Flask(__name__)
api = Api(app)

# Instantiate the cache
cache = Cache()
cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': './tmp'})

# global configuration variables
clientID=-1

# read database connection url from the environment variable we just set.
DATABASE_URL = os.environ.get('DATABASE_URL')
con = None
# Helper function provided by the teaching staff
def get_data_from_simulation(id):
    """Connects to the simulation and gets a float signal value

    Parameters
    ----------
    id : str
        The signal id in CoppeliaSim. Possible values are 'accelX', 'accelY' and 'accelZ'.

    Returns
    -------
    data : float
        The float value retrieved from the simulation. None if retrieval fails.
    """
    if clientID!=-1:
        res, data = sim.simxGetFloatSignal(clientID, id, sim.simx_opmode_blocking)
        if res==sim.simx_return_ok:
            return data
    return None

# TODO LAB 1 - Implement the data collection loop in a thread
class DataCollection(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # TODO LAB1 - initialize the "current_rate" value in the cache
        cache.set("current_rate", 1) # adds variable to memory
        # TODO LAB2 - initialize db connection

    def run(self):
        try:
            # create a new database connection by calling the connect() function
            con = psycopg2.connect(DATABASE_URL)
        except Exception as error:
            print('Cause: {}'.format(error))

        cursor = con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS accel (id SERIAL PRIMARY KEY, axis VARCHAR(1) NOT NULL, value FLOAT NOT NULL, ts TIMESTAMP DEFAULT NOW())")
        cursor.execute("CREATE TABLE IF NOT EXISTS timer (id SERIAL PRIMARY KEY, value FLOAT NOT NULL)")

        #timer = cache.get("current_rate")
        timer = 1
        while True:
            # TODO LAB 1 - Get acceleration data values (x, y and z) from the simulation in a cycle and print them to the console
            accX = get_data_from_simulation('accelX')#randrange(10)
            accY = get_data_from_simulation('accelY')#randrange(10)
            accZ = get_data_from_simulation('accelZ')#randrange(10)
            print("x: " + str(accX))
            print("y: " + str(accY))
            print("z: " + str(accZ))

            if accX != None and accY != None and accZ != None:
                # TODO LAB 2 - Insert the data into the PostgreSQL database on Heroku
                cursor.execute("INSERT INTO accel(id, axis, value, ts) VALUES (DEFAULT, 'x', %s, DEFAULT), (DEFAULT, 'y', %s, DEFAULT), (DEFAULT, 'z', %s, DEFAULT);"% (accX, accY, accZ))
                con.commit()
                
            #temp = cache.get("current_rate")
            postgreSQL_select_Query = "select * from timer"

            cursor.execute(postgreSQL_select_Query)
            mobile_records = cursor.fetchall()
            temp = None
            if len(mobile_records) - 1 >= 0:
                temp = mobile_records[len(mobile_records)-1][1]
                print("encontrou")
                
            if temp != None:
                timer = temp
            print("timer: "+str(timer))
            time.sleep(timer)
# TODO LAB 1 - Implement the UpdateRate resource
class UpdateRate(Resource):
    
    def put(self, id):
        cache.set("current_rate", id)

    
# TODO LAB 1 - Define the API resource routing
#api.add_resource...
api.add_resource(UpdateRate, '/update_rate/<int:id>')

if __name__ == '__main__':
    sim.simxFinish(-1) # just in case, close all opened connections
    clientID=sim.simxStart('127.0.0.1',19997,True,True,5243,5) # Connect to CoppeliaSim
    if clientID!=-1:
        # TODO LAB 1 - Start the data collection as a daemon thread
        dc = DataCollection() 
        dc.daemon = True
        dc.start()
        app.run(debug=True, threaded=True)
    else:
        exit()