// File: web/js/map-widget.js

/**
 * Business Finder Map Widget
 * Provides a user interface for selecting a location and radius on a map
 */

// Global variables
let map;
let marker;
let circle;
let currentLat = 37.7749;
let currentLng = -122.4194;
let currentRadius = 1000;
let searchTerm = 'business';

/**
 * Initialize the Google Map
 */
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: currentLat, lng: currentLng },
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: true,
        streetViewControl: false
    });

    // Create initial marker and circle
    createMarkerAndCircle(new google.maps.LatLng(currentLat, currentLng));

    // Add click listener to map
    map.addListener("click", (event) => {
        createMarkerAndCircle(event.latLng);
    });

    // Add radius slider listener
    document.getElementById("radius-slider").addEventListener("input", function() {
        currentRadius = parseInt(this.value);
        document.getElementById("radius-value").textContent = currentRadius;
        if (circle) {
            circle.setRadius(currentRadius);
        }
    });

    // Add search term input listener
    document.getElementById("search-term").addEventListener("input", function() {
        searchTerm = this.value || 'business';
    });

    // Add copy button listener
    document.getElementById("copy-button").addEventListener("click", function() {
        copyParametersToClipboard();
    });

    // Add download button listener if present
    const downloadButton = document.getElementById("download-button");
    if (downloadButton) {
        downloadButton.addEventListener("click", function() {
            downloadParametersAsFile();
        });
    }

    // Add run button listener if present
    const runButton = document.getElementById("run-button");
    if (runButton) {
        runButton.addEventListener("click", function() {
            sendParametersToBackend();
        });
    }
}

/**
 * Create or update the marker and circle on the map
 */
function createMarkerAndCircle(location) {
    // Update coordinates
    currentLat = location.lat();
    currentLng = location.lng();

    // Update display
    document.getElementById("lat-lng-display").textContent =
        `Latitude: ${currentLat.toFixed(6)}, Longitude: ${currentLng.toFixed(6)}`;

    // Remove previous marker and circle
    if (marker) marker.setMap(null);
    if (circle) circle.setMap(null);

    // Create new marker
    marker = new google.maps.Marker({
        position: location,
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP
    });

    // Create new circle
    circle = new google.maps.Circle({
        map: map,
        radius: currentRadius,
        fillColor: "#4285F4",
        fillOpacity: 0.2,
        strokeColor: "#4285F4",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        editable: true
    });

    // Bind circle to marker
    circle.bindTo('center', marker, 'position');

    // Add marker drag listener
    marker.addListener("dragend", (event) => {
        currentLat = event.latLng.lat();
        currentLng = event.latLng.lng();
        document.getElementById("lat-lng-display").textContent =
            `Latitude: ${currentLat.toFixed(6)}, Longitude: ${currentLng.toFixed(6)}`;
    });

    // Add circle radius change listener
    google.maps.event.addListener(circle, 'radius_changed', function() {
        currentRadius = Math.round(circle.getRadius());
        document.getElementById("radius-value").textContent = currentRadius;
        document.getElementById("radius-slider").value = currentRadius;
    });
}

/**
 * Get the current parameters as a JSON object
 */
function getParameters() {
    return {
        search_term: searchTerm,
        latitude: currentLat,
        longitude: currentLng,
        radius: currentRadius
    };
}

/**
 * Copy parameters to clipboard
 */
function copyParametersToClipboard() {
    const params = getParameters();
    const paramsString = JSON.stringify(params, null, 2);

    navigator.clipboard.writeText(paramsString)
        .then(() => {
            alert("Parameters copied to clipboard!");
        })
        .catch(err => {
            console.error('Failed to copy: ', err);

            // Fallback - create a temporary text area
            const textArea = document.createElement("textarea");
            textArea.value = paramsString;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                alert("Parameters copied to clipboard!");
            } catch (err) {
                console.error('Fallback: Oops, unable to copy', err);
                alert("Couldn't copy automatically. Please select and copy the text manually:\n\n" + paramsString);
            }
            document.body.removeChild(textArea);
        });
}

// Initialize map when the page loads
window.onload = function() {
    // If no API key is provided in the URL, show an error
    const urlParams = new URLSearchParams(window.location.search);
    const apiKey = urlParams.get('key');

    if (!apiKey) {
        document.getElementById("map").innerHTML =
            '<div style="padding: 20px; text-align: center;">' +
            '<h3>API Key Required</h3>' +
            '<p>Please provide a Google Maps API key in the URL: <code>?key=YOUR_API_KEY</code></p>' +
            '</div>';
    } else {
        // Load Google Maps API script
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
    }
};
