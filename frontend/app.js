// ==================================================
// Transit Intelligence Dashboard
// Frontend JavaScript
// ==================================================


// ==================================================
// Get HTML Elements
// ==================================================

const routeSelect =
    document.getElementById("route");

const directionSelect =
    document.getElementById("direction");

const stopSelect =
    document.getElementById("stop");
const routeSearch =
    document.getElementById("route-search");

const stopSearch =
    document.getElementById("stop-search");

let allRoutes = [];
let allStops = [];

// ==================================================
// Escape HTML
// Prevent unsafe HTML injection
// ==================================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ==================================================
// Convert GTFS Time to Minutes
// Supports times greater than 24:00:00
// ==================================================

function timeToMinutes(time) {

    const parts =
        time.split(":");

    const hours =
        parseInt(parts[0], 10);

    const minutes =
        parseInt(parts[1], 10);

    return hours * 60 + minutes;

}


// ==================================================
// Load Routes
// ==================================================

async function loadRoutes() {

    try {

        const mode =
            document.getElementById("mode").value;

        const response =
            await fetch(
                `/api/routes?mode=${encodeURIComponent(mode)}`
            );
        if (!response.ok) {

            throw new Error(
                "Could not load routes."
            );

        }

        const routes =
            await response.json();
        allRoutes = routes;

        routeSelect.innerHTML = `
            <option value="">
                Select a route
            </option>
        `;

        routes.forEach(route => {

            const option =
                document.createElement("option");

            option.value =
                route.route_short_name;

            option.textContent =
                `${route.route_short_name} - ${route.route_long_name}`;

            routeSelect.appendChild(option);

        });

    } catch (error) {

        console.error(
            "Error loading routes:",
            error
        );

        routeSelect.innerHTML = `
            <option value="">
                Could not load routes
            </option>
        `;
    }
}

function displayRoutes(routes) {

    routeSelect.innerHTML = `
        <option value="">
            Select a route
        </option>
    `;

    routes.forEach(route => {

        const option =
            document.createElement("option");

        option.value =
            route.route_short_name;

        option.textContent =
            `${route.route_short_name} - ${route.route_long_name}`;

        routeSelect.appendChild(option);
    });
}

// ==================================================
// Load Directions
// ==================================================

async function loadDirections() {

    const route =
        routeSelect.value;


    directionSelect.innerHTML = `
        <option value="">
            Select a direction
        </option>
    `;


    stopSelect.innerHTML = `
        <option value="">
            Select a stop
        </option>
    `;


    if (!route) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/routes/${encodeURIComponent(route)}/directions`
            );


        if (!response.ok) {

            throw new Error(
                "Could not load directions."
            );

        }


        const directions =
            await response.json();


        directions.forEach(direction => {

            const option =
                document.createElement("option");

            option.value =
                direction.direction_id;

            option.textContent =
                `${direction.direction_id} - ${direction.trip_headsign}`;

            directionSelect.appendChild(option);

        });

    } catch (error) {

        console.error(
            "Error loading directions:",
            error
        );

    }

}


// ==================================================
// Load Stops
// ==================================================

async function loadStops() {

    const route =
        routeSelect.value;

    const direction =
        directionSelect.value;


    stopSelect.innerHTML = `
        <option value="">
            Select a stop
        </option>
    `;


    if (!route || direction === "") {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/routes/${encodeURIComponent(route)}/stops` +
                `?direction=${encodeURIComponent(direction)}`
            );


        if (!response.ok) {

            throw new Error(
                "Could not load stops."
            );

        }


        const stops =
            await response.json();

        allStops = stops;


        stops.forEach(stop => {

            const option =
                document.createElement("option");

            option.value =
                stop.stop_id;

            option.textContent =
                stop.stop_name;

            stopSelect.appendChild(option);

        });

    } catch (error) {

        console.error(
            "Error loading stops:",
            error
        );

    }

}


// ==================================================
// Load Route Information
// ==================================================

async function loadRouteInformation() {

    const route =
        routeSelect.value;

    const routeInfo =
        document.getElementById("route-info");


    // Reset route information

    if (!route) {

        routeInfo.innerHTML = `

            <h2>
                Route Information
            </h2>

            <p>
                Select a route to view route information.
            </p>

        `;

        return;

    }


    try {

        const response =
            await fetch(
                `/api/routes/${encodeURIComponent(route)}/summary`
            );


        if (!response.ok) {

            throw new Error(
                "Could not load route information."
            );

        }


        const data =
            await response.json();

        // Display route information

        const selectedStopOption =
            stopSelect.options[stopSelect.selectedIndex];
        const selectedStop =
            stopSelect.value && selectedStopOption ?
            selectedStopOption.text :
            "";

        routeInfo.innerHTML = `
<h2>
    Route ${escapeHTML(data.route_short_name)}
</h2>

<p>
    ${escapeHTML(data.route_long_name)}
</p>
    

    ${
        selectedStop
            ? `
                <div class="route-card">
                    <strong>
                        Selected Stop
                    </strong>

                    <span>
                        ${escapeHTML(selectedStop)}
                    </span>

                    <p>
                        Direction:
                        ${escapeHTML(
                            directionSelect.options[
                                directionSelect.selectedIndex
                            ]?.text || ""
                        )}
                    </p>
                </div>
            `
            : ""
    }

    <div class="route-summary">

        ${data.directions.map(direction => `

            <div class="route-card">

                <strong>
                    Direction
                    ${escapeHTML(direction.direction_id)}
                </strong>

              <span>
    ${escapeHTML(direction.direction_name)}
</span>

                <p>
                    ${escapeHTML(direction.stop_count)}
                    stops
                </p>

                <p>
                    ${escapeHTML(direction.trip_count)}
                    trips
                </p>

            </div>

        `).join("")}

    </div>

`;
    }

    catch (error) {

        console.error(
            "Error loading route information:",
            error
        );


        routeInfo.innerHTML = `

            <h2>
                Route Information
            </h2>

            <p>
                Error: ${escapeHTML(error.message)}
            </p>

        `;

    }

}


// ==================================================
// Format Time
// ==================================================

function formatTime(time) {

    const parts =
        time.split(":");

    let hour =
        parseInt(parts[0], 10);

    const minute =
        parts[1];

    const period =
        hour >= 12 ? "PM" : "AM";


    // Handle GTFS times beyond 24 hours

    hour =
        hour % 24;


    if (hour === 0) {

        hour = 12;

    }

    else if (hour > 12) {

        hour -= 12;

    }


    return `${hour}:${minute} ${period}`;

}


// ==================================================
// Calculate Headways
// ==================================================

function calculateHeadways(departures) {

    const headways = [];


    for (
        let i = 1;
        i < departures.length;
        i++
    ) {

        const previous =
            departures[i - 1];

        const current =
            departures[i];


        const previousMinutes =
            timeToMinutes(previous);

        const currentMinutes =
            timeToMinutes(current);


        const difference =
            currentMinutes - previousMinutes;


        headways.push({

            from: previous,

            to: current,

            minutes: difference

        });

    }


    return headways;

}
// ==================================================
// Determine Service Period
// ==================================================

function getServicePeriod(time) {

    const minutes =
        timeToMinutes(time);

    // Morning Peak: 7:00 AM - 9:00 AM
    if (
        minutes >= 7 * 60 &&
        minutes < 9 * 60
    ) {

        return "Morning Peak";

    }

    // Midday / Off-Peak: 9:00 AM - 3:00 PM
    if (
        minutes >= 9 * 60 &&
        minutes < 15 * 60
    ) {

        return "Midday Off-Peak";

    }

    // Evening Peak: 3:00 PM - 6:00 PM
    if (
        minutes >= 15 * 60 &&
        minutes < 18 * 60
    ) {

        return "Evening Peak";

    }

    // Evening / Off-Peak
    return "Evening Off-Peak";
}
// ==================================================
// Analyze Service Periods
// ==================================================

function analyzeServicePeriods(departures) {

    const periods = {
        "Morning Peak": [],
        "Midday Off-Peak": [],
        "Evening Peak": [],
        "Evening Off-Peak": []
    };


    // Group departures into service periods

    departures.forEach(time => {

        const period =
            getServicePeriod(time);

        periods[period].push(time);

    });


    const analysis = {};


    // Calculate statistics for each period

    Object.entries(periods).forEach(
        ([periodName, periodDepartures]) => {

            const periodHeadways =
                calculateHeadways(periodDepartures);


            let averageHeadway = null;

            if (periodHeadways.length > 0) {

                const totalHeadway =
                    periodHeadways.reduce(
                        (sum, headway) =>
                            sum + headway.minutes,
                        0
                    );

                averageHeadway =
                    totalHeadway /
                    periodHeadways.length;

            }


            // Calculate service intensity
            // Number of departures per hour

            let serviceIntensity = 0;

            if (periodDepartures.length > 1) {

                const firstDeparture =
                    timeToMinutes(
                        periodDepartures[0]
                    );

                const lastDeparture =
                    timeToMinutes(
                        periodDepartures[
                            periodDepartures.length - 1
                        ]
                    );

                const durationHours =
                    (lastDeparture - firstDeparture) / 60;


                if (durationHours > 0) {

                    serviceIntensity =
                        (periodDepartures.length - 1) /
                        durationHours;

                }

            }


            analysis[periodName] = {

                departureCount:
                    periodDepartures.length,

                averageHeadway:
                    averageHeadway,

                serviceIntensity:
                    serviceIntensity

            };

        }
    );


    return analysis;
}
// ==================================================
// ==================================================
// Calculate Headway Statistics
// ==================================================

function calculateHeadwayStatistics(headways) {

    if (headways.length === 0) {

        return {
            shortest: null,
            longest: null
        };

    }

    const values =
        headways.map(headway => headway.minutes);


    return {

        shortest: Math.min(...values),

        longest: Math.max(...values)

    };

}


// ==================================================
// Draw Headway Chart
// ==================================================

function drawHeadwayChart(departures, headways) {

    const canvas =
        document.getElementById("headway-chart");


    if (!canvas) {

        return;

    }


    const existingChart =
        Chart.getChart(canvas);


    if (existingChart) {

        existingChart.destroy();

    }


    if (headways.length === 0) {

        return;

    }


    const labels = [];


    for (
        let i = 0;
        i < headways.length;
        i++
    ) {

        labels.push(
            `${formatTime(departures[i])} → ${formatTime(departures[i + 1])}`
        );

    }


    new Chart(canvas, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [

                {

                    label: "Headway (minutes)",

                    data:
                        headways.map(
                            headway => headway.minutes
                        ),

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true,

                    title: {

                        display: true,

                        text: "Minutes"

                    }

                },

                x: {

                    title: {

                        display: true,

                        text: "Departure Interval"

                    }

                }

            },

            plugins: {

                legend: {

                    display: true

                }

            }

        }

    });

}
// ==================================================
// Display Service Period Analysis
// ==================================================

function displayServicePeriodAnalysis(analysis) {

    const periods = {

        "Morning Peak": {
            departures: "morning-peak-departures",
            headway: "morning-peak-headway",
            intensity: "morning-peak-intensity"
        },

        "Midday Off-Peak": {
            departures: "midday-off-peak-departures",
            headway: "midday-off-peak-headway",
            intensity: "midday-off-peak-intensity"
        },

        "Evening Peak": {
            departures: "evening-peak-departures",
            headway: "evening-peak-headway",
            intensity: "evening-peak-intensity"
        },

        "Evening Off-Peak": {
            departures: "evening-off-peak-departures",
            headway: "evening-off-peak-headway",
            intensity: "evening-off-peak-intensity"
        }

    };


    Object.entries(periods).forEach(
        ([periodName, elementIds]) => {

            const data =
                analysis[periodName];


            if (!data) {
                return;
            }


            // Number of departures

            document.getElementById(
                elementIds.departures
            ).textContent =
                data.departureCount;


            // Average headway

document.getElementById(
    elementIds.headway
).textContent =
    data.departureCount > 0 && data.averageHeadway !== null
        ? data.averageHeadway.toFixed(2)
        : "No scheduled service";


// Service intensity

document.getElementById(
    elementIds.intensity
).textContent =
    data.departureCount > 0 && data.serviceIntensity > 0
        ? data.serviceIntensity.toFixed(2)
        : "No scheduled service";

}
    );
}
// ==================================================
// Calculate Frequency
// ==================================================

async function calculateFrequency() {

   const route =
    routeSelect.value;

   const mode =
    document.getElementById("mode").value;

    const direction =
    directionSelect.value;

    const stop =
        stopSelect.value;

    const day =
        document.getElementById("day").value;

    const startTime =
        document.getElementById("start-time").value;

    const endTime =
        document.getElementById("end-time").value;

    const result =
        document.getElementById("frequency-result");
// Check required selections
if (
    !route ||
    direction === "" ||
    !stop ||
    !day ||
    !startTime ||
    !endTime
) {
    result.innerHTML = `
        <h2>Frequency Analysis</h2>
        <p>
            Please select a route, direction, stop,
            day, start time, and end time.
        </p>
    `;
    return;
}

// Validate time range
if (startTime >= endTime) {
    result.innerHTML = `
        <h2>Frequency Analysis</h2>
        <p>End time must be later than start time.</p>
    `;
    return;
}

    

    // Show loading message

    result.innerHTML = `

        <h2>
            Frequency Analysis
        </h2>

        <p>
            Calculating frequency...
        </p>

    `;


    try {

        const response =
            await fetch(
                `/api/routes/${encodeURIComponent(route)}/frequency` +
                `?stop_id=${encodeURIComponent(stop)}` +
                `&day=${encodeURIComponent(day)}` +
               `&direction=${encodeURIComponent(direction)}` +
              `&mode=${encodeURIComponent(mode)}` +
               `&start=${encodeURIComponent(startTime)}:00` +
                `&end=${encodeURIComponent(endTime)}:00`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Could not calculate frequency."
            );

        }


    // Calculate individual headways

const headways =
    calculateHeadways(data.departures);

drawHeadwayChart(
    data.departures,
    headways
);

const headwayStatistics =
    calculateHeadwayStatistics(headways);


// Analyze peak and off-peak service periods

const servicePeriodAnalysis =
    analyzeServicePeriods(data.departures);

console.log(
    "Service Period Analysis:",
    servicePeriodAnalysis
);
displayServicePeriodAnalysis(
    servicePeriodAnalysis
);

// Check for long service gaps

        let longGapWarning = "";

        if (
            headwayStatistics.longest !== null &&
            headwayStatistics.longest >= 20
        ) {

            longGapWarning = `

                <div class="long-gap-warning">

                    ⚠ Long service gap detected:
                    ${headwayStatistics.longest} minutes
                    between departures.

                </div>

            `;

        }

        // Display results

        result.innerHTML = `

            <h2>
                Frequency Analysis
            </h2>

<div class="frequency-summary">


    <div class="frequency-card">

        <strong>
            Departures
        </strong>

        <span>
            ${data.departure_count}
        </span>

    </div>


    <div class="frequency-card">

        <strong>
            Average Headway
        </strong>

        <span>
    ${data.average_headway_minutes !== null
        ? data.average_headway_minutes.toFixed(2)
        : "N/A"}
    min
</span>

    </div>


    <div class="frequency-card">

        <strong>
            Median Headway
        </strong>

        <span>
    ${data.median_headway_minutes !== null
        ? data.median_headway_minutes.toFixed(1)
        : "N/A"}
    min
</span>

    </div>


    <div class="frequency-card">

        <strong>
            Shortest Gap
        </strong>

        <span>
            ${headwayStatistics.shortest !== null
                ? headwayStatistics.shortest + " min"
                : "N/A"
            }
        </span>

    </div>


    <div class="frequency-card">

        <strong>
            Longest Gap
        </strong>

        <span>
            ${headwayStatistics.longest !== null
                ? headwayStatistics.longest + " min"
                : "N/A"
            }
        </span>

    </div>


</div>
            ${longGapWarning}


            <h3>
                Departure Times
            </h3>


            <div class="departure-times">

                ${data.departures.map(time => `

                    <span class="departure">
                        ${formatTime(time)}
                    </span>

                `).join("")}

            </div>


            <h3>
                Headway Analysis
            </h3>


            <div class="headway-list">

                ${headways.length > 0

                    ? headways.map(headway => `

                        <div class="headway-item">

                            <span>
                                ${formatTime(headway.from)}
                                →
                                ${formatTime(headway.to)}
                            </span>

                            <strong>
                                ${headway.minutes} min
                            </strong>

                        </div>

                    `).join("")

                    : `

                        <p>
                            Not enough departures to calculate
                            individual headways.
                        </p>

                    `
                }

                        </div>


            <h3>
                Headway Visualization
            </h3>
<div class="headway-legend">

    <div class="legend-item">
        <span class="legend-box normal-gap"></span>
        Normal Gap (&lt; 30 min)
    </div>

    <div class="legend-item">
        <span class="legend-box long-gap"></span>
        Long Gap (≥ 30 min)
    </div>

</div>

            <div class="headway-chart">

    ${(() => {

        const maxHeadway =
            Math.max(...headways.map(h => h.minutes), 1);

        return headways.map(headway => {

            const width =
                (headway.minutes / maxHeadway) * 100;

            const warningClass =
                headway.minutes >= 30
                    ? " long-gap"
                    : "";

            return `

                <div class="headway-bar-row">

                    <span class="headway-label">
                        ${formatTime(headway.from)}
                        →
                        ${formatTime(headway.to)}
                    </span>

                    <div class="headway-bar-container">

                        <div
                            class="headway-bar${warningClass}"
                            style="width: ${width}%"
                        >
                        </div>

                    </div>

                    <strong class="headway-value">
                        ${headway.minutes} min
                    </strong>

                </div>

            `;

        }).join("");

    })()}

</div>
        `;

    }

    catch (error) {

        console.error(
            "Error calculating frequency:",
            error
        );


        result.innerHTML = `

            <h2>
                Frequency Analysis
            </h2>

            <p>
                Error: ${escapeHTML(error.message)}
            </p>

        `;

    }

}


// ==================================================
// Route Selection Event
// ==================================================
routeSelect.addEventListener("change", () => {
    loadDirections();
    loadRouteInformation();
});

directionSelect.addEventListener("change", loadStops);
stopSelect.addEventListener("change", () => {
    loadRouteInformation();
});

document.getElementById("mode").addEventListener(
    "change",
    () => {
        routeSelect.value = "";
        directionSelect.innerHTML = `
            <option value="">
                Select a direction
            </option>
        `;
        stopSelect.innerHTML = `
            <option value="">
                Select a stop
            </option>
        `;

        loadRoutes();
    }
);

loadRoutes();
routeSearch.addEventListener("input", () => {

    const searchTerm =
        routeSearch.value
            .toLowerCase()
            .trim();

    const filteredRoutes =
        allRoutes.filter(route =>
            String(route.route_short_name)
                .toLowerCase()
                .includes(searchTerm) ||

            String(route.route_long_name)
                .toLowerCase()
                .includes(searchTerm)
        );

    displayRoutes(filteredRoutes);
});
stopSearch.addEventListener("input", () => {

    const searchTerm =
        stopSearch.value
            .toLowerCase()
            .trim();

    const filteredStops =
        allStops.filter(stop =>
            String(stop.stop_name)
                .toLowerCase()
                .includes(searchTerm)
        );

    stopSelect.innerHTML = `
        <option value="">
            Select a stop
        </option>
    `;

    filteredStops.forEach(stop => {

        const option =
            document.createElement("option");

        option.value =
            stop.stop_id;

        option.textContent =
            stop.stop_name;

        stopSelect.appendChild(option);
    });
});
async function loadFeedInfo() {
    try {
        const response = await fetch("/api/feed-info");
        const data = await response.json();

        const formatDate = (dateString) => {
            const year = dateString.substring(0, 4);
            const month = dateString.substring(4, 6);
            const day = dateString.substring(6, 8);

            const date = new Date(`${year}-${month}-${day}T00:00:00`);

            return date.toLocaleDateString("en-CA", {
                year: "numeric",
                month: "long",
                day: "numeric"
            });
        };

        const status = document.getElementById("gtfs-data-status");

        status.textContent =
            `${data.publisher} feed version ${data.version} | ` +
            `Service period: ${formatDate(data.start_date)} – ${formatDate(data.end_date)}`;

    } catch (error) {
        console.error("Error loading GTFS feed information:", error);

        document.getElementById("gtfs-data-status").textContent =
            "GTFS feed information unavailable";
    }
}

loadFeedInfo();