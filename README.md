\# TransLink Transit Intelligence Dashboard

**Individual Continuation Project · INFO 4190 · Kwantlen Polytechnic University**

A GTFS-based transit intelligence dashboard that analyzes scheduled TransLink service and presents route, stop, frequency, headway, and peak/off-peak service information through an interactive web dashboard.

---

## Overview

The project transforms scheduled GTFS transit data into an interactive transit analysis system.

The implementation uses:

- **PostgreSQL** for GTFS data storage
- **Python** and **psycopg2** for database processing
- **Flask** for the REST API
- **HTML/CSS/JavaScript** for the dashboard
- **Chart.js** for data visualization

The primary demonstration route is **Route 401 — Brighouse Station/One Road**.

---

## System Architecture

```text
GTFS Data
    ↓
PostgreSQL Database
    ↓
Python / PostgreSQL Processing
    ↓
Flask REST API
    ↓
JavaScript Dashboard
    ↓
Transit Frequency & Headway Analysis
```

---

## Dashboard Features

The dashboard allows users to select:

- Transit mode
- Route
- Direction
- Stop
- Day of week
- Start time
- End time

The system then calculates:

- Scheduled departure count
- Average headway
- Median headway
- Shortest gap
- Longest gap
- Departure times
- Individual headways
- Long service gaps
- Service intensity
- Peak vs. off-peak performance

---

## Peak and Off-Peak Analysis

Scheduled service is divided into four service periods:

1. **Morning Peak**
2. **Midday Off-Peak**
3. **Evening Peak**
4. **Evening Off-Peak**

Each period provides departure counts, average headway, and service intensity in buses per hour.

---

## Database

The PostgreSQL database contains GTFS tables including:

- `routes`
- `stops`
- `trips`
- `calendar`
- `stop_times`

The `stop_times` table contains approximately **1.85 million records**.

GTFS schedule times are stored as text because GTFS allows times beyond `24:00:00`.

---

## Flask API

The backend provides REST endpoints for:

- Route information
- Route directions
- Route stops
- Route summaries
- Frequency analysis
- Stop information

Example endpoints:

```text
/api/routes/401/summary
/api/routes/401/stops?direction=0
/api/routes/401/frequency
```

---

## Testing and Validation

The implementation was tested using Route 401 and **Steveston Exchange @ Bay 2**.

### Normal Service

The dashboard successfully calculated scheduled departures, headways, and peak/off-peak service performance.

### No Service

A time range containing no scheduled departures correctly returned:

- 0 departures
- N/A headway statistics
- No false long-gap warning
- No scheduled service for all service periods

### Single Departure

A time range containing one departure correctly avoided calculating an individual headway.

### Multiple Departures

Multiple departures correctly produced average, median, shortest, and longest headways.

### Long Service Gap

The dashboard successfully detected a **32-minute scheduled gap**:

```text
3:24 PM → 3:56 PM
```

and displayed the long-service-gap warning.

---

## Demonstration Results

Example Route 401 analysis:

```text
Route: 401 - Brighouse Station/One Road
Direction: 401 Brighouse Station
Stop: Steveston Exchange @ Bay 2
Day: Monday
Time Range: 7:00 AM – 8:00 PM
```

Results:

```text
Departures:       50
Average Headway:  15.53 minutes
Median Headway:   15.0 minutes
Shortest Gap:     12 minutes
Longest Gap:      32 minutes
```

Peak/off-peak results:

```text
Morning Peak:        8 departures
Midday Off-Peak:    24 departures
Evening Peak:       11 departures
Evening Off-Peak:    7 departures
```

---

## Data Source

The project uses TransLink Open Data GTFS scheduled transit data.

Feed version:

```text
26APR_20260508
```

Service period:

```text
April 20, 2026 – June 7, 2026
```

---

## Data Limitations

This dashboard analyzes **scheduled GTFS service**.

It does not provide:

- Real-time vehicle locations
- Real-time delays
- Ridership
- Passenger demand
- Crowding
- Actual vehicle performance

Therefore, dashboard results represent **planned scheduled service**, not real-time transit conditions.

---

## Project Structure

```text
translink-transit-intelligence/
│
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── gtfs_processor.py
│   ├── postgres_processor.py
│   └── test_gtfs.py
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── .gitignore
└── README.md
```

---

## Running the Project

From the project directory:

```cmd
py -m py_compile backend\app.py
py backend\app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The PostgreSQL database must be running and configured before starting the Flask application.

---

## Project Status

**Implementation and validation completed.**

Completed components include:

- GTFS data integration
- PostgreSQL database integration
- Python database processing
- Flask REST API
- Interactive transit dashboard
- Frequency analysis
- Headway analysis
- Peak/off-peak analysis
- Long-gap detection
- Edge-case testing
- Final validation
- Git version control

The project is ready for demonstration and technical progress evaluation.