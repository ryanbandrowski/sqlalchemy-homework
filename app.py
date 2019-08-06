# import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model and reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Flask setup
app = Flask(__name__)

# setup the index route
@app.route("/")
def home():
    """List all available api routes, a note on date input format, and the range of available dates in the database."""
    session = Session(engine)
    # query the earliest and latest dates available in the database
    earliest_date = session.query(Measurement.date).order_by(Measurement.date).first()[0]
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # return the available routes, date format note, and available date range
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br>Note: dates are input in 'YYYY-MM-DD' format.<br>"
        f"<br>Database Date Range:<br>Earliest: {earliest_date}<br>Latest: {latest_date}"
    )

# setup the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last 12 months from most recent date in database"""
    session = Session(engine)
    # find the latest date and the date 1 year ago
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    year_ago = (dt.date(int(latest_date[0][0][0:4]), int(latest_date[0][0][6]), int(latest_date[0][0][8:10])) - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date.between(year_ago, latest_date)).all()
    # create a dictionary with the dates and precipitation data
    ltm_prcp = []
    for date, prcp in results:
        ltm_prcp_dict = {}
        ltm_prcp_dict["date"] = date
        ltm_prcp_dict["prcp"] = prcp
        ltm_prcp.append(ltm_prcp_dict)
    # return the JSSON dictionary
    return jsonify(ltm_prcp)

# setup the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the database"""
    session = Session(engine)
    # list the stations in the database
    results = session.query(Measurement.station).\
        group_by(Measurement.station).all()
    # convert the list of tuples into normal list
    stations = list(np.ravel(results))
    # return the JSON list
    return jsonify(stations)

# setup the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    session = Session(engine)
    # find the latest date and the date 1 year ago
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc())
    year_ago = (dt.date(int(latest_date[0][0][0:4]), int(latest_date[0][0][6]), int(latest_date[0][0][8:10])) - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    # list the dates and temperature observations for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date.between(year_ago, latest_date)).all()
    # convert the list of tuples into normal list
    tobs = list(np.ravel(results))
    # return the JSON list
    return jsonify(tobs)

# setup the start_date temperature calculations route
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Return JSON list of TMIN, TAVG, and TMAX for range containing all dates greater than/equal to the start date"""
    session = Session(engine)
    # query TMIN, TAVG, and TMAX for dates greather than the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    # convert the list of tuples into normal list
    start_tobs = list(np.ravel(results))
    # return the JSON list
    return jsonify(start_tobs)

# setup the start_date/end_date temperature calculations route
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    """Return JSON list of TMIN, TAVG, and TMAX for dates between the start and end date inclusive"""
    session = Session(engine)
    # query TMIN, TAVG, and TMAX for the range between the start and end dates inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    # convert the list of tuples into normal list
    trip_tobs = list(np.ravel(results))
    # return the JSON list
    return jsonify(trip_tobs)

# run the app
if __name__ == '__main__':
    app.run(debug=True)