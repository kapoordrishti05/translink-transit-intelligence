import pandas as pd

from db import get_connection


# --------------------------------------------------
# Route functions
# --------------------------------------------------

def load_routes():
    conn = get_connection()

    try:
        query = """
            SELECT
                route_id,
                route_short_name,
                route_long_name,
                route_type
            FROM routes
        """

        routes = pd.read_sql_query(query, conn)

        routes["route_id"] = routes["route_id"].astype(str).str.strip()
        routes["route_short_name"] = (
            routes["route_short_name"].astype(str).str.strip()
        )

        return routes

    finally:
        conn.close()


def find_route(routes, route_number):
    """
    Find a route using the public route number.
    """

    route_number = str(route_number).strip()

    return routes[
        routes["route_short_name"] == route_number
    ].copy()


# --------------------------------------------------
# Trip functions
# --------------------------------------------------

def get_route_trips(trips, route_id):
    """
    Get all trips belonging to a route.
    """

    route_id = str(route_id).strip()

    return trips[
        trips["route_id"] == route_id
    ].copy()


def load_route_trips(route_id):
    conn = get_connection()

    try:
        query = """
            SELECT
                route_id,
                service_id,
                trip_id,
                trip_headsign,
                trip_short_name,
                direction_id,
                block_id,
                shape_id,
                wheelchair_accessible,
                bikes_allowed
            FROM trips
            WHERE route_id = %s
        """

        trips = pd.read_sql_query(
            query,
            conn,
            params=[str(route_id).strip()]
        )

        trips["route_id"] = trips["route_id"].astype(str).str.strip()
        trips["trip_id"] = trips["trip_id"].astype(str).str.strip()
        trips["service_id"] = trips["service_id"].astype(str).str.strip()

        return trips

    finally:
        conn.close()


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


def load_route_stop_times(route_id):
    conn = get_connection()

    try:
        query = """
            SELECT
                st.trip_id,
                st.arrival_time,
                st.departure_time,
                st.stop_id,
                st.stop_sequence,
                t.direction_id,
                t.trip_headsign
            FROM stop_times st
            JOIN trips t
                ON st.trip_id = t.trip_id
            WHERE t.route_id = %s
        """

        stop_times = pd.read_sql_query(
            query,
            conn,
            params=[str(route_id).strip()]
        )

        stop_times["trip_id"] = (
            stop_times["trip_id"].astype(str).str.strip()
        )

        stop_times["stop_id"] = (
            stop_times["stop_id"].astype(str).str.strip()
        )

        return stop_times

    finally:
        conn.close()


# --------------------------------------------------
# Stop functions
# --------------------------------------------------

def load_stops():
    conn = get_connection()

    try:
        query = """
            SELECT
                stop_id,
                stop_name,
                stop_lat,
                stop_lon
            FROM stops
        """

        stops = pd.read_sql_query(query, conn)

        stops["stop_id"] = (
            stops["stop_id"].astype(str).str.strip()
        )

        return stops

    finally:
        conn.close()


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
# Calendar functions
# --------------------------------------------------

def load_calendar():
    conn = get_connection()

    try:
        query = """
            SELECT
                service_id,
                monday,
                tuesday,
                wednesday,
                thursday,
                friday,
                saturday,
                sunday,
                start_date,
                end_date
            FROM calendar
        """

        calendar = pd.read_sql_query(query, conn)

        calendar["service_id"] = (
            calendar["service_id"].astype(str).str.strip()
        )

        return calendar

    finally:
        conn.close()


def get_service_ids_for_day(calendar, day):
    """
    Get service IDs that operate on a specific day.
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


# --------------------------------------------------
# Time conversion
# --------------------------------------------------

def time_to_minutes(time_string):
    """
    Convert a GTFS time such as 07:12:00 into minutes.

    Supports GTFS times greater than 24:00:00.
    """

    hours, minutes, seconds = map(
        int,
        str(time_string).split(":")
    )

    return hours * 60 + minutes + seconds / 60


# --------------------------------------------------
# PostgreSQL frequency calculation
# --------------------------------------------------

def calculate_frequency(
    stop_id,
    route_id,
    direction_id=None,
    start_time=None,
    end_time=None,
    day=None
):
    """
    Calculate scheduled frequency directly from PostgreSQL.
    """

    conn = get_connection()

    try:

        query = """
            SELECT
                st.trip_id,
                st.departure_time,
                t.direction_id,
                t.trip_headsign
            FROM stop_times st
            JOIN trips t
                ON st.trip_id = t.trip_id
            JOIN calendar c
                ON t.service_id = c.service_id
            WHERE t.route_id = %s
              AND st.stop_id = %s
        """

        params = [
            str(route_id).strip(),
            str(stop_id).strip()
        ]

        # --------------------------------------------------
        # Day filter
        # --------------------------------------------------

        if day is not None:

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

            query += f"""
                AND c.{day} = 1
            """

        # --------------------------------------------------
        # Direction filter
        # --------------------------------------------------

        if direction_id is not None:

            query += """
                AND t.direction_id = %s
            """

            params.append(int(direction_id))

        # --------------------------------------------------
        # Time filters
        #
        # departure_time is TEXT because GTFS can contain
        # values such as 24:00:30.
        # PostgreSQL INTERVAL preserves this correctly.
        # --------------------------------------------------

        if start_time is not None:

            query += """
                AND st.departure_time::interval >= %s::interval
            """

            params.append(str(start_time))

        if end_time is not None:

            query += """
                AND st.departure_time::interval < %s::interval
            """

            params.append(str(end_time))

        # --------------------------------------------------
        # Correct GTFS time ordering
        # --------------------------------------------------

        query += """
            ORDER BY st.departure_time::interval
        """

        data = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        # --------------------------------------------------
        # Calculate frequency
        # --------------------------------------------------

        data["departure_minutes"] = (
            data["departure_time"]
            .apply(time_to_minutes)
        )

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

            average_headway = None
            median_headway = None
            shortest_gap = None
            longest_gap = None

        return {
            "stop_id": str(stop_id).strip(),

            "direction_id": direction_id,

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

    finally:
        conn.close()