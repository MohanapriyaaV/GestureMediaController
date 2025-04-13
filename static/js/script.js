
// Update the status periodically
function updateStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => {
            // Update status indicator and text
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const songInfo = document.getElementById('song-info');
            const currentGesture = document.getElementById('current-gesture');
            
            // Update status indicator color and text
            statusIndicator.className = 'status-indicator';
            if (data.status === 'playing') {
                statusIndicator.classList.add('playing');
                statusText.textContent = 'Playing';
            } else if (data.status === 'paused') {
                statusIndicator.classList.add('paused');
                statusText.textContent = 'Paused';
            } else {
                statusText.textContent = 'Stopped';
            }
            
            // Update song info
            songInfo.textContent = data.song;
            
            // Update current gesture (capitalize first letter)
            if (data.gesture) {
                currentGesture.textContent = data.gesture.charAt(0).toUpperCase() + data.gesture.slice(1);
            } else {
                currentGesture.textContent = 'None';
            }
        })
        .catch(error => console.error('Error fetching status:', error));
}

// Control player function
function controlPlayer(action) {
    fetch(`/control/${action}`)
        .then(response => response.json())
        .then(data => {
            // Update immediately for more responsive UI
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const songInfo = document.getElementById('song-info');
            
            statusIndicator.className = 'status-indicator';
            if (data.status === 'playing') {
                statusIndicator.classList.add('playing');
                statusText.textContent = 'Playing';
            } else if (data.status === 'paused') {
                statusIndicator.classList.add('paused');
                statusText.textContent = 'Paused';
            } else {
                statusText.textContent = 'Stopped';
            }
            
            songInfo.textContent = data.song;
        })
        .catch(error => console.error('Error controlling player:', error));
}

// Update status every second
setInterval(updateStatus, 1000);

// Initial status update
document.addEventListener('DOMContentLoaded', updateStatus);
        