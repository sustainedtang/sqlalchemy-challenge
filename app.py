import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#Setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Routes:"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")


# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation Data"""
    # Query all Precipitation
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-24").\
        all()

    session.close()
# Return the JSON representation of your dictionary.    
    precipitation_data = []
    for date,prcp  in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
               
        precipitation_data.append(prcp_dict)
    return jsonify(precipitation_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query all Stations
    results = session.query(Station.station).\
                 order_by(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all TOBs"""
    # Query all tobs

    results = session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()

    session.close()
 # Convert the list to Dictionary
    tobs_all = []
    for prcp, date,tobs in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    session = Session(engine)
    start = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs).\
               filter(Measurement.date >= start))
    session.close()
    start_tobs_list = []   
    for min, avg, max in start:
        dict = {}
        dict["TMIN"] = min                     
        dict["TAVG"] = avg
        dict["TMAX"] = max
        start_tobs_list.append(dict)
    return jsonify(start_tobs_list)     


# Create our session (link) from Python to the DB
@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    
    session = Session(engine)

    """Return a list of min, avg and max tobs for start and end dates"""
    # Query all tobs

    end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date <= end).all()
    start = session.query(func.avg(Measurement.tobs),func.max(Measurement.tobs),func.min(Measurement.tobs).\
               filter(Measurement.date >= start))
    session.close()
  
    # Create a dictionary from the row data and append to a list of start_end_date_tobs
    end_tobs = []
    for min, avg, max in end:
        end_tobs_dict = {}
        end_tobs_dict["TMIN"] = min
        end_tobs_dict["TMAX"] = max
        end_tobs_dict["TAVG"] = avg
        end_tobs.append(end_tobs_dict) 
    start_tobs_list = []   
    for min, avg, max in start:
        dict = {}
        dict["TMIN"] = min                     
        dict["TMAX"] = max
        dict["TAVG"] = avg
        start_tobs_list.append(dict)
    return jsonify(start_tobs_list, end_tobs)  
if __name__ == "__main__":
    app.run(debug=True)