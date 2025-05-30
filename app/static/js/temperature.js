let isCelsius = true;
let temperatureChart;
let rawData = [];  // Store the raw data in Celsius
let originalTemp;  // Will be initialized from data attribute
let refreshInterval;  // Will be initialized from data attribute
let temperatureThreshold;  // Will be initialized from data attribute

function celsiusToFahrenheit(celsius) {
    return (celsius * 9/5) + 32;
}

function toggleUnit() {
    const tempValue = document.getElementById('temperature-value');
    const tempUnit = document.getElementById('temperature-unit');
    const toggleButton = document.querySelector('.unit-toggle');
    
    if (isCelsius) {
        // Convert to Fahrenheit
        const fahrenheit = celsiusToFahrenheit(originalTemp);
        tempValue.textContent = fahrenheit.toFixed(1);
        tempUnit.textContent = '°F';
        toggleButton.textContent = 'Switch to °C';
    } else {
        // Convert back to Celsius
        tempValue.textContent = originalTemp.toFixed(1);
        tempUnit.textContent = '°C';
        toggleButton.textContent = 'Switch to °F';
    }
    
    isCelsius = !isCelsius;
    updateChartDisplay();
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function updateLatestTemperature() {
    console.log('Fetching latest temperature...');
    fetch('/temperature/latest')
        .then(response => response.json())
        .then(data => {
            console.log('Received temperature data:', data);
            const tempValue = document.getElementById('temperature-value');
            const timestamp = document.querySelector('.timestamp');
            
            // Update temperature display
            originalTemp = data.temperature;  // Update the global originalTemp
            tempValue.textContent = isCelsius ? 
                data.temperature.toFixed(1) : 
                celsiusToFahrenheit(data.temperature).toFixed(1);
            
            // Update timestamp
            timestamp.textContent = `Last updated: ${new Date(data.collected_at).toLocaleString()}`;
            
            // Update body class for background color
            document.body.classList.remove('alert', 'normal', 'transition');
            if (data.is_alert) {
                document.body.classList.add('alert');
            } else if (data.is_normal) {
                document.body.classList.add('normal');
            } else {
                document.body.classList.add('transition');
            }
            
            console.log('Temperature updated successfully');
        })
        .catch(error => {
            console.error('Error fetching latest temperature:', error);
        });
}

function updateChartData() {
    console.log('Fetching chart data...');
    fetch('/temperature/hourly')
        .then(response => response.json())
        .then(data => {
            console.log('Received chart data:', data);
            rawData = data;  // Store raw data
            updateChartDisplay();
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
}

function updateChartDisplay() {
    if (!rawData.length) {
        console.log('No chart data available');
        return;
    }

    // Reverse the data arrays to show latest data on the right
    const labels = rawData.map(reading => formatTime(reading.collected_at)).reverse();
    const temperatures = rawData.map(reading => 
        isCelsius ? reading.temperature : celsiusToFahrenheit(reading.temperature)
    ).reverse();

    if (temperatureChart) {
        temperatureChart.data.labels = labels;
        temperatureChart.data.datasets[0].data = temperatures;
        temperatureChart.data.datasets[0].label = isCelsius ? 'Temperature (°C)' : 'Temperature (°F)';
        temperatureChart.data.datasets[1].data = Array(labels.length).fill(
            isCelsius ? temperatureThreshold : celsiusToFahrenheit(temperatureThreshold)
        );
        temperatureChart.data.datasets[1].label = isCelsius ? 
            `Threshold (${temperatureThreshold}°C)` : 
            `Threshold (${celsiusToFahrenheit(temperatureThreshold).toFixed(1)}°F)`;
        temperatureChart.update();
        console.log('Chart updated with new data');
    } else {
        const ctx = document.getElementById('temperatureChart').getContext('2d');
        temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: isCelsius ? 'Temperature (°C)' : 'Temperature (°F)',
                    data: temperatures,
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: isCelsius ? 
                        `Threshold (${temperatureThreshold}°C)` : 
                        `Threshold (${celsiusToFahrenheit(temperatureThreshold).toFixed(1)}°F)`,
                    data: Array(labels.length).fill(
                        isCelsius ? temperatureThreshold : celsiusToFahrenheit(temperatureThreshold)
                    ),
                    borderColor: '#FF5252',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
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
        console.log('Chart initialized');
    }
}

function getNextUpdateTime() {
    // If we have raw data, use the latest reading's timestamp
    if (rawData && rawData.length > 0) {
        const latestReading = rawData[0];  // Latest reading is at index 0
        const lastUpdateTime = new Date(latestReading.collected_at);
        const nextUpdate = new Date(lastUpdateTime);
        nextUpdate.setMinutes(lastUpdateTime.getMinutes() + refreshInterval);
        nextUpdate.setSeconds(2);
        nextUpdate.setMilliseconds(0);
        console.log('Existing Data! Setting Next Update Time', {
            nextUpdate
        });
        return nextUpdate;
    }
    
    // Fallback to current time if no data is available
    const now = new Date();
    const nextUpdate = new Date(now);
    nextUpdate.setMinutes(now.getMinutes() + refreshInterval);
    nextUpdate.setSeconds(2);
    nextUpdate.setMilliseconds(0);
    console.log('No data! Setting Next Update Time', {
        nextUpdate
    });
    return nextUpdate;
}

function scheduleNextUpdate() {
    const nextUpdate = getNextUpdateTime();
    const now = new Date();
    const delay = nextUpdate.getTime() - now.getTime();
    
    // Update the refresh info display
    updateRefreshInfo(nextUpdate);
    
    // Schedule the next update
    setTimeout(() => {
        updateLatestTemperature();
        updateChartData();
        scheduleNextUpdate();  // Schedule the next update after this one
    }, delay);
}

function updateRefreshInfo(nextUpdate) {
    const refreshInfo = document.getElementById('refresh-info');
    refreshInfo.textContent = `Next update at ${nextUpdate.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page initialized');
    
    // Get initial values from data attributes
    originalTemp = parseFloat(document.body.dataset.temperature);
    refreshInterval = parseInt(document.body.dataset.refreshInterval) / 60000; // Convert from milliseconds to minutes
    temperatureThreshold = parseFloat(document.body.dataset.threshold);
    const isAlert = document.body.dataset.isAlert === 'true';
    const isNormal = document.body.dataset.isNormal === 'true';
    
    console.log('Initial values:', {
        originalTemp,
        refreshInterval,
        temperatureThreshold,
        isAlert,
        isNormal
    });
    
    // Set initial body class based on temperature state
    if (isAlert) {
        document.body.classList.add('alert');
    } else if (isNormal) {
        document.body.classList.add('normal');
    } else {
        document.body.classList.add('transition');
    }

    // Initial data load
    updateLatestTemperature();
    updateChartData();
    
    // Start the update scheduling
    scheduleNextUpdate();
    console.log(`Update scheduling started with interval of ${refreshInterval} minutes`);
}); 