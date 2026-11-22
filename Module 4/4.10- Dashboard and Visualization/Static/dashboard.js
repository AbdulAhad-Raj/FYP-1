
// ============================================================
// SENTINEL-X DASHBOARD
// Live API Integration and Visualization
// ============================================================

let sensorChart = null;

// ------------------------------------------------------------
// FORMAT VALUES
// ------------------------------------------------------------

function formatCoordinate(value) {
    return Number(value).toFixed(3) + " m";
}

function formatRSSI(value) {
    return Number(value).toFixed(1) + " dBm";
}


// ------------------------------------------------------------
// LOAD SYSTEM SUMMARY
// ------------------------------------------------------------

async function loadSummary() {

    try {

        const response = await fetch("/api/summary");

        if (!response.ok) {
            throw new Error("Summary API request failed");
        }

        const data = await response.json();

        if (data.status !== "success") {
            throw new Error("Invalid summary response");
        }

        document.getElementById("assetCount").textContent =
            data.total_assets;

        document.getElementById("positionCount").textContent =
            data.total_positions;

        const latest = data.latest_position;

        if (latest) {

            document.getElementById("coordinateX").textContent =
                formatCoordinate(latest.x_m);

            document.getElementById("coordinateY").textContent =
                formatCoordinate(latest.y_m);

            document.getElementById("mapAssetId").textContent =
                latest.asset_id;

            document.getElementById("mapX").textContent =
                formatCoordinate(latest.x_m);

            document.getElementById("mapY").textContent =
                formatCoordinate(latest.y_m);

            updateAssetMarker(latest.x_m, latest.y_m);

        }

        document.getElementById("lastUpdated").textContent =
            "Last database record: " +
            (latest ? latest.timestamp : "No records available");

    } catch (error) {

        console.error("Summary error:", error);

        document.getElementById("lastUpdated").textContent =
            "Unable to retrieve summary data";

    }

}


// ------------------------------------------------------------
// UPDATE ASSET POSITION ON MAP
// ------------------------------------------------------------

function updateAssetMarker(x, y) {

    const marker = document.getElementById("assetMarker");

    // Calibrated test area: approximately -0.23 to +0.23 m.
    // Map coordinates are clamped to keep the marker visible.

    const xValue = Math.max(-0.23, Math.min(0.23, Number(x)));
    const yValue = Math.max(-0.23, Math.min(0.23, Number(y)));

    const left = 50 + (xValue / 0.23) * 30;
    const top = 50 - (yValue / 0.23) * 30;

    marker.style.left = left + "%";
    marker.style.top = top + "%";

}


// ------------------------------------------------------------
// LOAD FOUR-SENSOR RSSI DATA
// ------------------------------------------------------------

async function loadSensors() {

    try {

        const response = await fetch("/api/sensors");

        if (!response.ok) {
            throw new Error("Sensor API request failed");
        }

        const data = await response.json();

        if (data.status !== "success") {
            throw new Error("Invalid sensor response");
        }

        const sensorGrid = document.getElementById("sensorGrid");

        sensorGrid.innerHTML = "";

        const labels = [];
        const values = [];

        data.sensors.forEach(sensor => {

            labels.push(sensor.location);
            values.push(sensor.rssi);

            const card = document.createElement("div");

            card.className = "sensor-card";

            card.innerHTML = `
                <span>${sensor.location} Sensor</span>
                <h2>${formatRSSI(sensor.rssi)}</h2>
                <small>${sensor.sensor_id}</small>
            `;

            sensorGrid.appendChild(card);

        });

        updateSensorChart(labels, values);

    } catch (error) {

        console.error("Sensor error:", error);

    }

}


// ------------------------------------------------------------
// CREATE / UPDATE SENSOR CHART
// ------------------------------------------------------------

function updateSensorChart(labels, values) {

    const context = document
        .getElementById("sensorChart")
        .getContext("2d");

    if (sensorChart) {

        sensorChart.data.labels = labels;
        sensorChart.data.datasets[0].data = values;

        sensorChart.update();

        return;

    }

    sensorChart = new Chart(context, {

        type: "bar",

        data: {

            labels: labels,

            datasets: [{

                label: "RSSI (dBm)",

                data: values,

                backgroundColor: [
                    "#4b85d8",
                    "#57b69a",
                    "#e5ad65",
                    "#9678ce"
                ],

                borderRadius: 7,

                borderSkipped: false

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: true,

            plugins: {

                legend: {
                    display: false
                }

            },

            scales: {

                y: {

                    min: -100,
                    max: 0,

                    title: {
                        display: true,
                        text: "Signal Strength (dBm)"
                    }

                },

                x: {

                    grid: {
                        display: false
                    }

                }

            }

        }

    });

}


// ------------------------------------------------------------
// LOAD POSITION HISTORY
// ------------------------------------------------------------

async function loadHistory() {

    try {

        const response = await fetch("/api/positions");

        if (!response.ok) {
            throw new Error("Position history request failed");
        }

        const data = await response.json();

        if (data.status !== "success") {
            throw new Error("Invalid history response");
        }

        const table = document.getElementById("historyTable");

        table.innerHTML = "";

        if (data.positions.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="5">No position records found</td>
                </tr>
            `;

            return;

        }

        data.positions.forEach(position => {

            const row = document.createElement("tr");

            const cells = [
                position.position_id,
                position.timestamp,
                position.asset_id,
                formatCoordinate(position.x_m),
                formatCoordinate(position.y_m)
            ];

            cells.forEach(value => {

                const cell = document.createElement("td");

                cell.textContent = value;

                row.appendChild(cell);

            });

            table.appendChild(row);

        });

    } catch (error) {

        console.error("History error:", error);

    }

}


// ------------------------------------------------------------
// REFRESH DASHBOARD
// ------------------------------------------------------------

async function refreshDashboard() {

    await Promise.all([
        loadSummary(),
        loadSensors(),
        loadHistory()
    ]);

}


// ------------------------------------------------------------
// INITIALIZE DASHBOARD
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    console.log("SENTINEL-X dashboard initialized");

    refreshDashboard();

    // Refresh database information every 3 seconds.
    setInterval(refreshDashboard, 3000);

});
