from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import pandas as pd

from postgres_processor import (
    calculate_frequency,
    load_routes,
    load_route_trips,
    load_route_stop_times,
    load_stops
)


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_FOLDER = str(PROJECT_ROOT / "frontend")


# --------------------------------------------------
# Load GTFS data once when the application starts
# --------------------------------------------------

FEED_INFO_FILE = (
    PROJECT_ROOT
    / "Tests_Run_on_Data"
    / "google_transit"
    / "feed_info.txt"
)

feed_info = pd.read_csv(FEED_INFO_FILE)


# --------------------------------------------------
# Feed information
# --------------------------------------------------

@app.route("/api/feed-info")
def get_feed_info():

    info = feed_info.iloc[0]

    return jsonify({
        "publisher": str(info["feed_publisher_name"]),
        "publisher_url": str(info["feed_publisher_url"]),
        "start_date": str(info["feed_start_date"]),
        "end_date": str(info["feed_end_date"]),
        "version": str(info["feed_version"])
    })


# --------------------------------------------------
# Frontend
# --------------------------------------------------

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/app.js")
def javascript():

    return send_from_directory(
        FRONTEND_FOLDER,
        "app.js"
    )


@app.route("/style.css")
def stylesheet():

    return send_from_directory(
        FRONTEND_FOLDER,
        "style.css"
    )

# --------------------------------------------------
# Get all routes
# --------------------------------------------------

@app.route("/api/routes")
def get_routes():

    mode = request.args.get("mode")

    route_list = load_routes()

    if mode == "bus":

        route_list = route_list[
            route_list["route_type"] == 3
        ].copy()

    route_list = route_list[
        [
            "route_id",
            "route_short_name",
            "route_long_name",
            "route_type"
        ]
    ].fillna("")

    return jsonify(
        route_list.to_dict("records")
    )


# --------------------------------------------------
# Get directions for a route
# --------------------------------------------------

@app.route("/api/routes/<route>/directions")

def get_route_directions(route):

    # Load routes from PostgreSQL
    route_list = load_routes()

    # Find route using the visible route number, e.g. 401
    route_data = route_list[
        route_list["route_short_name"].astype(str).str.strip()
        == str(route).strip()
    ].copy()

    if route_data.empty:
        return jsonify({
            "error": f"Route {route} not found"
        }), 404

    # Get actual GTFS route_id, e.g. 6722
    route_id = str(
        route_data.iloc[0]["route_id"]
    )

    # Load trips from PostgreSQL
    route_trips = load_route_trips(route_id)

    directions = (
        route_trips[
            [
                "direction_id",
                "trip_headsign"
            ]
        ]
        .drop_duplicates()
        .sort_values("direction_id")
    )

    return jsonify(
        directions.to_dict("records")
    )
# --------------------------------------------------
# Get stops for a route and direction
# --------------------------------------------------

@app.route("/api/routes/<route>/stops")
def get_route_stops_api(route):

    direction = request.args.get("direction")

    if direction is None:
        return jsonify({
            "error": "direction is required"
        }), 400

    # Load routes from PostgreSQL
    route_list = load_routes()

    route_data = route_list[
        route_list["route_short_name"].astype(str).str.strip()
        == str(route).strip()
    ].copy()

    if route_data.empty:
        return jsonify({
            "error": f"Route {route} not found"
        }), 404

    route_id = str(
        route_data.iloc[0]["route_id"]
    )

    # Load trips from PostgreSQL
    route_trips = load_route_trips(route_id)

    direction_trips = route_trips[
        route_trips["direction_id"].astype(str)
        == str(direction)
    ].copy()

    if direction_trips.empty:
        return jsonify({
            "error": (
                f"Direction {direction} "
                f"not found for route {route}"
            )
        }), 404

    # Load stop times from PostgreSQL
    route_stop_times = load_route_stop_times(route_id)

    # Use one representative trip to preserve stop order
    representative_trip_id = str(
        direction_trips["trip_id"].iloc[0]
    )

    trip_stops = route_stop_times[
        route_stop_times["trip_id"].astype(str)
        == representative_trip_id
    ].copy()

    trip_stops = trip_stops.sort_values(
        "stop_sequence"
    )

    # Load stops from PostgreSQL
    stop_data = load_stops()

    stop_data["stop_id"] = (
        stop_data["stop_id"]
        .astype(str)
        .str.strip()
    )

    trip_stops["stop_id"] = (
        trip_stops["stop_id"]
        .astype(str)
        .str.strip()
    )

    route_stops = trip_stops[
        [
            "stop_id",
            "stop_sequence"
        ]
    ].merge(
        stop_data,
        on="stop_id",
        how="left"
    )

    route_stops = route_stops[
        [
            "stop_id",
            "stop_sequence",
            "stop_name",
            "stop_lat",
            "stop_lon"
        ]
    ].copy()

    route_stops = route_stops.fillna("")

    return jsonify(
        route_stops.to_dict("records")
    )
# --------------------------------------------------
# Calculate route frequency
# --------------------------------------------------
@app.route("/api/routes/<route>/frequency")
def route_frequency(route):

    stop_id = request.args.get("stop_id")
    day = request.args.get("day")
    direction = request.args.get("direction")
    mode = request.args.get("mode")
    start_time = request.args.get("start")
    end_time = request.args.get("end")

    if stop_id is None:
        return jsonify({
            "error": "stop_id is required"
        }), 400

    if day is None:
        return jsonify({
            "error": "day is required"
        }), 400

    if direction is None:
        return jsonify({
            "error": "direction is required"
        }), 400

    if mode is None:
        return jsonify({
            "error": "mode is required"
        }), 400

    # Load routes from PostgreSQL
    route_list = load_routes()

    # Find visible route number, e.g. 401
    route_data = route_list[
        route_list["route_short_name"].astype(str).str.strip()
        == str(route).strip()
    ].copy()

    if route_data.empty:
        return jsonify({
            "error": f"Route {route} not found"
        }), 404

    # Get actual GTFS route_id
    route_id = str(
        route_data.iloc[0]["route_id"]
    )

    # Load trips from PostgreSQL
    route_trips = load_route_trips(route_id)

    # Filter selected direction
    direction_trips = route_trips[
        route_trips["direction_id"].astype(str)
        == str(direction)
    ].copy()

    if direction_trips.empty:
        return jsonify({
            "error": (
                f"Direction {direction} "
                f"not found for route {route}"
            )
        }), 404

    # Load stop times from PostgreSQL
    route_stop_times = load_route_stop_times(route_id)

    # Keep only trips for selected direction
    direction_stop_times = route_stop_times[
        route_stop_times["trip_id"].isin(
            direction_trips["trip_id"]
        )
    ].copy()

    direction_stop_ids = (
        direction_stop_times["stop_id"]
        .astype(str)
        .str.strip()
        .unique()
    )

    # Validate selected stop
    if str(stop_id).strip() not in direction_stop_ids:
        return jsonify({
            "error": (
                f"Stop {stop_id} does not belong to "
                f"route {route} direction {direction}"
            )
        }), 400

    try:
        frequency = calculate_frequency(
            stop_id=stop_id,
            route_id=route_id,
            direction_id=direction,
            start_time=start_time,
            end_time=end_time,
            day=day
        )

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    departures = [
        departure["departure_time"].strip()
        for departure in frequency["departures"]
    ]

    return jsonify({
        "route": route,
        "stop_id": stop_id,
        "direction": direction,
        "day": day,

        "departure_count":
            frequency["departure_count"],

        "average_headway_minutes": (
            round(
                frequency["average_headway_minutes"],
                2
            )
            if frequency["average_headway_minutes"]
            is not None
            else None
        ),

        "median_headway_minutes": (
            round(
                frequency["median_headway_minutes"],
                2
            )
            if frequency["median_headway_minutes"]
            is not None
            else None
        ),

        "departures": departures
    })


# # --------------------------------------------------
# Get information for a specific stop
# --------------------------------------------------
@app.route("/api/stops/<stop_id>")
def get_stop(stop_id):

    stop_id = str(stop_id).strip()

    # Load stops from PostgreSQL
    stop_list = load_stops()

    # Find selected stop
    stop_data = stop_list[
        stop_list["stop_id"].astype(str).str.strip()
        == stop_id
    ].copy()

    if stop_data.empty:
        return jsonify({
            "error": f"Stop {stop_id} not found"
        }), 404

    stop_data = stop_data[
        [
            "stop_id",
            "stop_name",
            "stop_lat",
            "stop_lon"
        ]
    ].fillna("")

    return jsonify(
        stop_data.iloc[0].to_dict()
    )

# --------------------------------------------------
# Get route summary
# --------------------------------------------------

@app.route("/api/routes/<route>/summary")
def route_summary(route):

    # Load routes from PostgreSQL
    route_list = load_routes()

    # Find the user-facing route number
    route_data = route_list[
        route_list["route_short_name"].astype(str).str.strip()
        == str(route).strip()
    ].copy()

    if route_data.empty:
        return jsonify({
            "error": f"Route {route} not found"
        }), 404

    # Get actual GTFS route_id
    route_id = str(route_data.iloc[0]["route_id"])

    route_short_name = str(
        route_data.iloc[0]["route_short_name"]
    )

    route_long_name = str(
        route_data.iloc[0]["route_long_name"]
    )

    # Load trips from PostgreSQL
    route_trips = load_route_trips(route_id)

    if route_trips.empty:
        return jsonify({
            "route_id": route_id,
            "route_short_name": route_short_name,
            "route_long_name": route_long_name,
            "directions": []
        })

    # Load stop times from PostgreSQL
    route_stop_times = load_route_stop_times(route_id)

    directions = []

    for direction_id, direction_trips in route_trips.groupby(
        "direction_id"
    ):

        trip_count = len(direction_trips)

        direction_stop_times = route_stop_times[
            route_stop_times["trip_id"].isin(
                direction_trips["trip_id"]
            )
        ]

        stop_count = direction_stop_times[
            "stop_id"
        ].nunique()

        headsign = (
            direction_trips["trip_headsign"]
            .dropna()
        )

        if len(headsign) > 0:
            direction_name = str(
                headsign.iloc[0]
            )
        else:
            direction_name = (
                f"Direction {direction_id}"
            )

        directions.append({
            "direction_id": int(direction_id),
            "direction_name": direction_name,
            "stop_count": int(stop_count),
            "trip_count": int(trip_count)
        })

    return jsonify({
        "route_id": route_id,
        "route_short_name": route_short_name,
       "route_long_name": route_long_name,
        "directions": directions
    })
# --------------------------------------------------
# Start Flask application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )