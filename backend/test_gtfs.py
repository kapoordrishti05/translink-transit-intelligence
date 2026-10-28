import pandas as pd

from gtfs_processor import (
    load_gtfs,
    find_route,
    get_route_trips,
    get_route_stop_times,
    get_route_stops,
    calculate_frequency,
    get_service_ids_for_day
)


# --------------------------------------------------
# Load GTFS data
# --------------------------------------------------

routes, trips, stop_times, stops, calendar = load_gtfs()

print("GTFS data loaded successfully.")
print()


# --------------------------------------------------
# Test service-day filtering
# --------------------------------------------------

print("========================================")
print("Service Day Test")
print("========================================")

monday_services = get_service_ids_for_day(
    calendar,
    "monday"
)

saturday_services = get_service_ids_for_day(
    calendar,
    "saturday"
)

sunday_services = get_service_ids_for_day(
    calendar,
    "sunday"
)

print("Monday service IDs:", monday_services)
print("Saturday service IDs:", saturday_services)
print("Sunday service IDs:", sunday_services)

print()


# --------------------------------------------------
# Test Route 401
# --------------------------------------------------

route = find_route(routes, "401")

print("Route 401:")

print(
    route[
        [
            "route_id",
            "route_short_name",
            "route_long_name"
        ]
    ]
)

print()


# --------------------------------------------------
# Get Route 401 trips
# --------------------------------------------------

route_id = route.iloc[0]["route_id"]

route_trips = get_route_trips(
    trips,
    route_id
)

print("Number of Route 401 trips:")
print(len(route_trips))

print()


# --------------------------------------------------
# Get Route 401 stop times
# --------------------------------------------------

route_stop_times = get_route_stop_times(
    stop_times,
    route_trips["trip_id"]
)

print("Number of Route 401 stop-time records:")
print(len(route_stop_times))

print()


# --------------------------------------------------
# Get Route 401 stops
# --------------------------------------------------

route_stops = get_route_stops(
    stops,
    route_stop_times["stop_id"].unique()
)

print("Number of Route 401 stops:")
print(len(route_stops))

print()


# --------------------------------------------------
# Test Route 410
# --------------------------------------------------

route_410 = find_route(routes, "410")

print("Route 410:")

print(
    route_410[
        [
            "route_id",
            "route_short_name",
            "route_long_name"
        ]
    ]
)


# --------------------------------------------------
# Route 401 Monday Frequency
# --------------------------------------------------

frequency = calculate_frequency(
    route_trips=route_trips,
    route_stop_times=route_stop_times,
    stop_id="6482",
    direction_id=0,
    start_time="07:00:00",
    end_time="09:00:00",
    day="monday",
    calendar=calendar
)

print()
print("========================================")
print("Route 401 Monday Frequency")
print("========================================")

print("Stop ID:", frequency["stop_id"])
print("Direction:", frequency["direction_id"])

print(
    "Number of departures:",
    frequency["departure_count"]
)

print(
    "Average headway:",
    frequency["average_headway_minutes"]
)

print(
    "Median headway:",
    frequency["median_headway_minutes"]
)

print()
print("Departures:")

for departure in frequency["departures"]:

    print(
        departure["departure_time"],
        "-",
        departure["trip_headsign"]
    )


# --------------------------------------------------
# Check duplicate departures
# --------------------------------------------------

print()
print("========================================")
print("Duplicate Departure Check")
print("========================================")

departure_times = [
    departure["departure_time"]
    for departure in frequency["departures"]
]

duplicate_times = (
    pd.Series(departure_times)
    .value_counts()
)

duplicate_times = duplicate_times[
    duplicate_times > 1
]

print("Duplicate departure times:")

print(duplicate_times)


# --------------------------------------------------
# Route 410 Monday Frequency
# --------------------------------------------------

print()
print("========================================")
print("Route 410 Monday Frequency")
print("========================================")

route_410_id = route_410.iloc[0]["route_id"]

route_410_trips = get_route_trips(
    trips,
    route_410_id
)

print("Number of Route 410 trips:")
print(len(route_410_trips))

route_410_stop_times = get_route_stop_times(
    stop_times,
    route_410_trips["trip_id"]
)

print("Number of Route 410 stop-time records:")
print(len(route_410_stop_times))

route_410_stop_id = (
    route_410_stop_times["stop_id"]
    .value_counts()
    .index[0]
)

print(
    "Testing Route 410 at stop:",
    route_410_stop_id
)

frequency_410 = calculate_frequency(
    route_trips=route_410_trips,
    route_stop_times=route_410_stop_times,
    stop_id=route_410_stop_id,
    direction_id=0,
    start_time="07:00:00",
    end_time="09:00:00",
    day="monday",
    calendar=calendar
)

print()

print(
    "Stop ID:",
    frequency_410["stop_id"]
)

print(
    "Direction:",
    frequency_410["direction_id"]
)

print(
    "Number of departures:",
    frequency_410["departure_count"]
)

print(
    "Average headway:",
    frequency_410["average_headway_minutes"]
)

print(
    "Median headway:",
    frequency_410["median_headway_minutes"]
)

print()
print("Departures:")

for departure in frequency_410["departures"]:

    print(
        departure["departure_time"],
        "-",
        departure["trip_headsign"]
    )


# --------------------------------------------------
# Route 401 Weekend Frequency
# --------------------------------------------------

print()
print("========================================")
print("Route 401 Weekend Frequency")
print("========================================")

for day in ["saturday", "sunday"]:

    weekend_frequency = calculate_frequency(
        route_trips=route_trips,
        route_stop_times=route_stop_times,
        stop_id="6482",
        direction_id=0,
        start_time="07:00:00",
        end_time="09:00:00",
        day=day,
        calendar=calendar
    )

    print()
    print(day.capitalize() + ":")

    print(
        "Service IDs:",
        weekend_frequency["service_ids"]
    )

    print(
        "Number of departures:",
        weekend_frequency["departure_count"]
    )

    print(
        "Average headway:",
        weekend_frequency["average_headway_minutes"]
    )

    print(
        "Median headway:",
        weekend_frequency["median_headway_minutes"]
    )

    print()
    print("Departures:")

    for departure in weekend_frequency["departures"]:

        print(
            departure["departure_time"],
            "-",
            departure["trip_headsign"]
        )


# --------------------------------------------------
# Route 401 Direction 1 Frequency
# --------------------------------------------------

print()
print("========================================")
print("Route 401 Direction 1 Frequency")
print("========================================")

frequency_401_direction_1 = calculate_frequency(
    route_trips=route_trips,
    route_stop_times=route_stop_times,
    stop_id="10582",
    direction_id=1,
    start_time="07:00:00",
    end_time="09:00:00",
    day="monday",
    calendar=calendar
)

print(
    "Stop ID:",
    frequency_401_direction_1["stop_id"]
)

print(
    "Direction:",
    frequency_401_direction_1["direction_id"]
)

print(
    "Number of departures:",
    frequency_401_direction_1["departure_count"]
)

print(
    "Average headway:",
    frequency_401_direction_1["average_headway_minutes"]
)

print(
    "Median headway:",
    frequency_401_direction_1["median_headway_minutes"]
)

print()
print("Departures:")

for departure in frequency_401_direction_1["departures"]:

    print(
        departure["departure_time"],
        "-",
        departure["trip_headsign"]
    )