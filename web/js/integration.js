// File: web/js/integration.js

/**
 * Business Finder Integration
 * Provides integration between the map widget and the Python backend
 */

/**
 * Download parameters as a JSON file
 */
function downloadParametersAsFile() {
    const params = getParameters();
    const paramsString = JSON.stringify(params, null, 2);

    // Create a Blob with the JSON content
    const blob = new Blob([paramsString], { type: 'application/json' });

    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'business-finder-params.json';

    // Trigger a click event on the anchor
    document.body.appendChild(a);
    a.click();

    // Clean up
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
}

/**
 * Send parameters to backend for processing
 * This function would be implemented if using a web service approach
 */
function sendParametersToBackend() {
    const params = getParameters();
    const apiKey = document.getElementById('api-key').value;

    if (!apiKey) {
        alert('Please enter your Google API key');
        return;
    }

    // Show loading state
    const runButton = document.getElementById('run-button');
    const originalText = runButton.textContent;
    runButton.textContent = 'Processing...';
    runButton.disabled = true;

    // Prepare data to send
    const requestData = {
        ...params,
        api_key: apiKey,
        output_format: document.getElementById('output-format').value || 'csv'
    };

    // Send data to backend
    fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link for the file
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `business-results.${requestData.output_format}`;

        // Trigger download
        document.body.appendChild(a);
        a.click();

        // Clean up
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);

        // Reset button
        runButton.textContent = originalText;
        runButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);

        // Reset button
        runButton.textContent = originalText;
        runButton.disabled = false;
    });
}

/**
 * Generate command line string for running the Python script
 */
function generateCommandLine() {
    const params = getParameters();
    const apiKey = document.getElementById('api-key').value || 'YOUR_API_KEY';

    const commandElement = document.getElementById('command-line');
    if (commandElement) {
        const command = `business-finder search --api-key "${apiKey}" --json-params '${JSON.stringify(params)}'`;
        commandElement.textContent = command;
    }
}

// Update command line when parameters change
if (document.getElementById('update-command')) {
    document.getElementById('update-command').addEventListener('click', generateCommandLine);
}