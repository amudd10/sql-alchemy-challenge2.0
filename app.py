# Dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt   
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine,reflect = True)

# Save references to each table 
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask 
app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Homepage for Hawaii Climate Analysis API!<br/>"
        f"The Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    query_date = dt.date(2017,8,23)-dt.timedelta(days=365)
    year_prcp_data = (session.query(Measurement.date, Measurement.prcp)
                  .filter(Measurement.date > query_date)
                  .all())
    session.close()

    prcp_dict = dict(year_prcp_data)

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_names = session.query(Station.name).all()
    session.close()

     # Convert list of tuples into normal list
    all_names = list(np.ravel(stations_names))
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017,8,23)-dt.timedelta(days=365)
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    most_active_station = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), 
                    func.avg(Measurement.tobs)).\
                    filter(Measurement.station == 'USC00519281').all()
    tobs_data = (session.query(Measurement.date, Measurement.tobs)
                  .filter(Measurement.date > query_date)
                  .filter(Measurement.station=='USC00519281')
                  .all())

    session.close()

    tobs = dict(tobs_data)

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def starts(start):
    user_input1 = start
    session1 = Session(engine)
    all_dates_q = session1.query(Measurement.date).all()
    all_dates = list(np.ravel(all_dates_q))
    # calculate TMIN, TAVG, TMAX for dates greater than start
    start_data = session1.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= user_input1).all()
    session1.close()
    start_date_list = list(np.ravel(start_data))
    start_dict = {"TMIN": start_date_list[0]}, {"TMAX": start_date_list[1]}, {"TAVG": start_date_list[2]}
    if user_input1 not in all_dates:
        return jsonify({"Error": "Input date not found"})
    else:
        return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    user_input2 = start
    user_input3 = end
    session2 = Session(engine)
    all_dates_r = session2.query(Measurement.date).all()
    all_dates2 = list(np.ravel(all_dates_r))
    # calculate TMIN, TAVG, TMAX for dates greater than start
    start_end_data = session2.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= user_input2).filter(Measurement.date <=user_input3).all()
    session2.close()
    start_end_datelist = list(np.ravel(start_end_data))
    start_end_dict =  {"TMIN": start_end_datelist[0]}, {"TMAX": start_end_datelist[1]}, {"TAVG": start_end_datelist[2]}
    if (user_input2 or user_input3) not in start_end_datelist:
        return jsonify({"Error": "Input date(s) not found"})
    else:
        return jsonify(start_end_dict)



if __name__ == '__main__':
    app.run(debug=True)