import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# At root, give all the links
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/Y-m-d<br/>"
        
        f"/api/v1.0/Y-m-d/Y-m-d"
    )

# Precipitation query
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query all measurement data
    results = session.query(Measurement).all()

    # Generate a dictionary. Create the key and give the precipitation data.
    precip = {}
    for i in results:
        precip[f"{i.date}"]=i.prcp
    
    return jsonify(precip)

# Station query
@app.route("/api/v1.0/stations")
def station():
    
    # Query stations and names
    results = session.query(Station.station, Station.name).all()

    return jsonify(results)

# Tempreture query
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Get the one year back date
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    oneyearback=dt.datetime.strptime(lastdate[0], "%Y-%m-%d")-dt.timedelta(days=366)

    # Query the date and tempreture for one year measurement data
    results = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= oneyearback).order_by(Measurement.date).all()

    # Generate a dictionary. Create the key and give the tobs data.
    tobsdata = {}
    for i in results:
        tobsdata[f"{i.date}"]=i.tobs
    
    return jsonify(tobsdata)

# Start date tempreture calculation
@app.route("/api/v1.0/<start>")
def startdate(start):

    # Query the min, avg, and max tempretures from the start date to the end of the date in the database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results=session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()

    # Give a dictionary to show the data
    showdata = {'T_min':results[0][0],'T_avg':results[0][1],'T_max':results[0][2]}
    return jsonify(showdata)
    
#  Start and end date tempreture calculation
@app.route("/api/v1.0/<start>/<end>")
def tripdate(start,end):

    # Query the min, avg, and max tempretures from the start date to the end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results=session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).all()
    
    # Give a dictionary to show the data
    showdata = {'T_min':results[0][0],'T_avg':results[0][1],'T_max':results[0][2]}
    return jsonify(showdata)
    

if __name__ == "__main__":
    app.run(debug=True)