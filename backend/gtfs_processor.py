from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GTFS_FOLDER = PROJECT_ROOT / "Tests_Run_on_Data" / "google_transit"


# --------------------------------------------------
# Load GTFS data
# --------------------------------------------------

def load_gtfs():
    """
    Load the GTFS files needed by the transit application.
    """

    routes = pd.read_csv(
        GTFS_FOLDER / "routes.txt"
    )

    trips = pd.read_csv(
        GTFS_FOLDER / "trips.txt"
    )

    stop_times = pd.read_csv(
        GTFS_FOLDER / "stop_times.txt",
        usecols=[
            "trip_id",
            "arrival_time",
            "departure_time",
            "stop_id",
            "stop_sequence"
        ]
    )

    stops = pd.read_csv(
        GTFS_FOLDER / "stops.txt",
        usecols=[
            "stop_id",
            "stop_name",
            "stop_lat",
            "stop_lon"
        ]
    )

    calendar = pd.read_csv(
        GTFS_FOLDER / "calendar.txt"
    )

    # Normalize important ID columns
    routes["route_id"] = (
        routes["route_id"].astype(str).str.strip()
    )

    routes["route_short_name"] = (
        routes["route_short_name"].astype(str).str.strip()
    )

    trips["route_id"] = (
        trips["route_id"].astype(str).str.strip()
    )

    trips["trip_id"] = (
        trips["trip_id"].astype(str).str.strip()
    )

    trips["service_id"] = (
        trips["service_id"].astype(str).str.strip()
    )

    stop_times["trip_id"] = (
        stop_times["trip_id"].astype(str).str.strip()
    )

    stop_times["stop_id"] = (
        stop_times["stop_id"].astype(str).str.strip()
    )

    stops["stop_id"] = (
        stops["stop_id"].astype(str).str.strip()
    )

    calendar["service_id"] = (
     calendar["service_id"].astype(str).str.strip()
    )

    print("Route columns:", routes.columns.tolist())
    print("Route types:")
    print(
        routes[
            [
                "route_short_name",
                "route_long_name",
                "route_type"
            ]
        ].head(20)
    )

    return routes, trips, stop_times, stops, calendar

# --------------------------------------------------
# Route functions
# --------------------------------------------------

def find_route(routes, route_number):
    """
    Find a route using the public route number.

    Example:
        401 -> Route 401
        410 -> Route 410
    """

    route_number = str(route_number).strip()

    return routes[
        routes["route_short_name"] == route_number
    ].copy()


def get_route_trips(trips, route_id):
    """
    Get all trips belonging to a route.
    """

    route_id = str(route_id).strip()

    return trips[
        trips["route_id"] == route_id
    ].copy()


# --------------------------------------------------
# Stop-time functions
# --------------------------------------------------

def get_route_stop_times(stop_times, trip_ids):
    """
    Get stop-time records belonging to a collection of trips.
    """

    trip_ids = (
        pd.Series(trip_ids)
        .astype(str)
        .str.strip()
    )

    return stop_times[
        stop_times["trip_id"].isin(trip_ids)
    ].copy()


# --------------------------------------------------
# Stop functions
# --------------------------------------------------

def get_route_stops(stops, stop_ids):
    """
    Get stop information for a collection of stop IDs.
    """

    stop_ids = (
        pd.Series(stop_ids)
        .astype(str)
        .str.strip()
    )

    return stops[
        stops["stop_id"].isin(stop_ids)
    ].copy()
# --------------------------------------------------
# Frequency calculation
# --------------------------------------------------
# --------------------------------------------------
# Service-day functions
# --------------------------------------------------

def get_service_ids_for_day(calendar, day):
    """
    Get service IDs that operate on a specific day.

    day can be:
        monday
        tuesday
        wednesday
        thursday
        friday
        saturday
        sunday
    """

    day = str(day).lower().strip()

    valid_days = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    }

    if day not in valid_days:
        raise ValueError(
            "Invalid day. Use Monday, Tuesday, Wednesday, "
            "Thursday, Friday, Saturday, or Sunday."
        )

    active_services = calendar[
        calendar[day] == 1
    ].copy()

    return active_services["service_id"].astype(str).tolist()
def time_to_minutes(time_string):
    """
    Convert a GTFS time such as 07:12:00 into minutes after midnight.

    GTFS can also contain times greater than 24:00:00,
    so this does not use datetime.time().
    """

    hours, minutes, seconds = map(
        int,
        str(time_string).split(":")
    )

    return hours * 60 + minutes + seconds / 60

def calculate_frequency(
    route_trips,
    route_stop_times,
    stop_id,
    direction_id=None,
    start_time=None,
    end_time=None,
    service_ids=None,
    day=None,
    calendar=None
):
    """
    Calculate scheduled frequency/headway for a selected stop.

    Parameters:
        route_trips:
            Trips belonging to the selected route.

        route_stop_times:
            Stop-time records belonging to those trips.

        stop_id:
            Stop where frequency should be measured.

        direction_id:
            Optional direction filter.

        start_time:
            Optional starting time, e.g. "07:00:00".

        end_time:
            Optional ending time, e.g. "09:00:00".

        service_ids:
            Optional list of service IDs.

        day:
            Optional weekday such as "monday" or "saturday".

        calendar:
            GTFS calendar DataFrame. Required when day is provided.
    """

    # --------------------------------------------------
    # Determine service IDs
    # --------------------------------------------------

    if day is not None:

        if calendar is None:
            raise ValueError(
                "calendar is required when day is provided."
            )

        service_ids = get_service_ids_for_day(
            calendar,
            day
        )

    # --------------------------------------------------
    # Filter trips by service
    # --------------------------------------------------

    trips = route_trips.copy()

    if service_ids is not None:

        service_ids = (
            pd.Series(service_ids)
            .astype(str)
            .str.strip()
            .tolist()
        )

        trips["service_id"] = (
            trips["service_id"]
            .astype(str)
            .str.strip()
        )

        trips = trips[
            trips["service_id"].isin(service_ids)
        ].copy()

    # --------------------------------------------------
    # Filter stop-time records
    # --------------------------------------------------

    data = route_stop_times.copy()

    data["stop_id"] = (
        data["stop_id"]
        .astype(str)
        .str.strip()
    )

    stop_id = str(stop_id).strip()

    data = data[
        data["stop_id"] == stop_id
    ].copy()

    # --------------------------------------------------
    # Keep only trips that passed service filtering
    # --------------------------------------------------

    data = data[
        data["trip_id"].isin(trips["trip_id"])
    ].copy()

    # --------------------------------------------------
    # Join direction information
    # --------------------------------------------------

    data = data.merge(
        trips[
            [
                "trip_id",
                "direction_id",
                "trip_headsign"
            ]
        ],
        on="trip_id",
        how="left"
    )

    # --------------------------------------------------
    # Filter direction
    # --------------------------------------------------

    if direction_id is not None:

        data = data[
            data["direction_id"].astype(str)
            == str(direction_id)
        ].copy()

    # --------------------------------------------------
    # Convert departure time
    # --------------------------------------------------

    data["departure_minutes"] = (
        data["departure_time"]
        .apply(time_to_minutes)
    )

    # --------------------------------------------------
    # Filter time window
    # --------------------------------------------------

    if start_time is not None:

        start_minutes = time_to_minutes(start_time)

        data = data[
            data["departure_minutes"] >= start_minutes
        ]

    if end_time is not None:

        end_minutes = time_to_minutes(end_time)

        data = data[
            data["departure_minutes"] < end_minutes
        ]

    # --------------------------------------------------
    # Sort departures
    # --------------------------------------------------

    data = data.sort_values(
        "departure_minutes"
    ).reset_index(drop=True)

    # -
        # --------------------------------------------------
    # Calculate headways
    # --------------------------------------------------

    if len(data) >= 2:

        data["headway_minutes"] = (
            data["departure_minutes"].diff()
        )

        headways = data["headway_minutes"].iloc[1:]

        average_headway = headways.mean()
        median_headway = headways.median()
        shortest_gap = headways.min()
        longest_gap = headways.max()

    else:

        data["headway_minutes"] = None

        average_headway = None
        median_headway = None
        shortest_gap = None
        longest_gap = None

    # --------------------------------------------------
    # Return results
    # --------------------------------------------------

    return {
        "stop_id": stop_id,
        "direction_id": direction_id,
        "service_ids": (
            service_ids
            if service_ids is not None
            else []
        ),

        "departure_count": len(data),

        "average_headway_minutes": average_headway,
        "median_headway_minutes": median_headway,
        "shortest_gap_minutes": shortest_gap,
        "longest_gap_minutes": longest_gap,

        "departures": data[
            [
                "trip_id",
                "departure_time",
                "direction_id",
                "trip_headsign"
            ]
        ].to_dict("records")
    }