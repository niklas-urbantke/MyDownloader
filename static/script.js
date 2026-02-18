// Socket.IO Connection
const socket = io();

// DOM Elements
const playlistUrlInput = document.getElementById('playlistUrl');
const loadBtn = document.getElementById('loadBtn');
const startBtn = document.getElementById('startBtn');
const newDownloadBtn = document.getElementById('newDownloadBtn');
const infoBox = document.getElementById('infoBox');
const playlistName = document.getElementById('playlistName');
const playlistInfo = document.getElementById('playlistInfo');
const downloadSection = document.getElementById('downloadSection');
const progressSection = document.getElementById('progressSection');
const completionSection = document.getElementById('completionSection');
const overallProgress = document.getElementById('overallProgress');
const overallPercentage = document.getElementById('overallPercentage');
const progressText = document.getElementById('progressText');
const currentSong = document.getElementById('currentSong');
const songList = document.getElementById('songList');
const completionText = document.getElementById('completionText');
const folderPath = document.getElementById('folderPath');
const ffmpegStatus = document.getElementById('ffmpegStatus');

// State
let currentPlaylistUrl = '';
let playlistData = null;
let songStatuses = {};

// Check FFmpeg on load
window.addEventListener('DOMContentLoaded', () => {
    checkFFmpeg();
});

// Check FFmpeg availability
async function checkFFmpeg() {
    try {
        const response = await fetch('/check_ffmpeg');
        const data = await response.json();
        
        const statusIndicator = ffmpegStatus.querySelector('.status-indicator');
        const statusDot = ffmpegStatus.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('span');
        
        if (data.available) {
            statusDot.classList.add('ready');
            statusText.textContent = 'FFmpeg bereit';
        } else {
            statusDot.classList.add('error');
            statusText.textContent = 'FFmpeg nicht verfügbar';
            showNotification('FFmpeg nicht gefunden. Bitte installieren!', 'error');
        }
    } catch (error) {
        console.error('FFmpeg check failed:', error);
        const statusDot = ffmpegStatus.querySelector('.status-dot');
        const statusText = ffmpegStatus.querySelector('span');
        statusDot.classList.add('error');
        statusText.textContent = 'FFmpeg-Status unbekannt';
    }
}

// Load Playlist
loadBtn.addEventListener('click', async () => {
    const url = playlistUrlInput.value.trim();
    
    if (!url) {
        showNotification('Bitte eine URL eingeben', 'error');
        return;
    }
    
    // Disable button and show loading
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<div class="loading"></div> Lädt...';
    
    try {
        const response = await fetch('/load_playlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentPlaylistUrl = url;
            playlistData = data;
            
            // Show info box
            playlistName.textContent = data.playlist_name;
            playlistInfo.textContent = `${data.song_count} Songs gefunden`;
            infoBox.style.display = 'block';
            downloadSection.style.display = 'block';
            
            showNotification('Playlist erfolgreich geladen!', 'success');
        } else {
            showNotification(data.error || 'Fehler beim Laden der Playlist', 'error');
        }
    } catch (error) {
        console.error('Load error:', error);
        showNotification('Verbindungsfehler', 'error');
    } finally {
        loadBtn.disabled = false;
        loadBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            </svg>
            Playlist laden
        `;
    }
});

// Start Download
startBtn.addEventListener('click', async () => {
    if (!currentPlaylistUrl) {
        showNotification('Bitte zuerst eine Playlist laden', 'error');
        return;
    }
    
    startBtn.disabled = true;
    startBtn.innerHTML = '<div class="loading"></div> Startet...';
    
    try {
        const response = await fetch('/start_download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: currentPlaylistUrl }),
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Hide previous sections
            downloadSection.style.display = 'none';
            
            // Show progress section
            progressSection.style.display = 'block';
            songList.innerHTML = '';
            songStatuses = {};
        } else {
            showNotification(data.error || 'Fehler beim Starten des Downloads', 'error');
            startBtn.disabled = false;
            startBtn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Download starten
            `;
        }
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Verbindungsfehler', 'error');
        startBtn.disabled = false;
    }
});

// New Download Button
newDownloadBtn.addEventListener('click', () => {
    // Reset everything
    completionSection.style.display = 'none';
    downloadSection.style.display = 'none';
    progressSection.style.display = 'none';
    infoBox.style.display = 'none';
    playlistUrlInput.value = '';
    currentPlaylistUrl = '';
    playlistData = null;
    songStatuses = {};
    songList.innerHTML = '';
    
    // Reset progress
    overallProgress.style.width = '0%';
    overallPercentage.textContent = '0%';
    progressText.textContent = '0 von 0 Songs';
    currentSong.textContent = '-';
    
    // Re-enable start button
    startBtn.disabled = false;
    startBtn.innerHTML = `
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polygon points="5 3 19 12 5 21 5 3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Download starten
    `;
});

// Socket.IO Event Handlers
socket.on('download_started', (data) => {
    console.log('Download started:', data);
    progressText.textContent = `0 von ${data.total} Songs`;
});

socket.on('progress_update', (data) => {
    console.log('Progress update:', data);
    
    // Update overall progress
    overallProgress.style.width = `${data.percentage}%`;
    overallPercentage.textContent = `${data.percentage}%`;
    progressText.textContent = `${data.current} von ${data.total} Songs`;
    currentSong.textContent = data.current_song;
});

socket.on('song_status', (data) => {
    console.log('Song status:', data);
    
    const songId = data.song;
    
    // Create or update song item
    if (!songStatuses[songId]) {
        songStatuses[songId] = data.status;
        addSongItem(data);
    } else {
        songStatuses[songId] = data.status;
        updateSongItem(data);
    }
});

socket.on('download_completed', (data) => {
    console.log('Download completed:', data);
    
    // Hide progress section
    progressSection.style.display = 'none';
    
    // Show completion section
    completionSection.style.display = 'block';
    completionText.textContent = `${data.total} Songs erfolgreich verarbeitet`;
    folderPath.textContent = data.folder;
    
    showNotification('Download abgeschlossen!', 'success');
});

socket.on('status_update', (data) => {
    console.log('Status:', data.message);
});

socket.on('error', (data) => {
    console.error('Error:', data.message);
    showNotification(data.message, 'error');
});

// Helper Functions
function addSongItem(data) {
    const item = document.createElement('div');
    item.className = 'song-item';
    item.id = `song-${getSongId(data.song)}`;
    
    const icon = getSongStatusIcon(data.status);
    
    item.innerHTML = `
        <div class="song-item-info">
            ${icon}
            <div>
                <div class="song-name">${escapeHtml(data.song)}</div>
                <div class="song-message">${escapeHtml(data.message)}</div>
            </div>
        </div>
    `;
    
    songList.appendChild(item);
    
    // Scroll to bottom
    songList.scrollTop = songList.scrollHeight;
}

function updateSongItem(data) {
    const item = document.getElementById(`song-${getSongId(data.song)}`);
    if (!item) return;
    
    const icon = getSongStatusIcon(data.status);
    const messageEl = item.querySelector('.song-message');
    const iconEl = item.querySelector('svg');
    
    if (messageEl) {
        messageEl.textContent = data.message;
    }
    
    if (iconEl) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = icon;
        iconEl.replaceWith(tempDiv.firstElementChild);
    }
}

function getSongStatusIcon(status) {
    const icons = {
        searching: `<svg class="song-status-icon status-downloading" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path d="M12 6v6l4 2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>`,
        downloading: `<svg class="song-status-icon status-downloading" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        </svg>`,
        success: `<svg class="song-status-icon status-success" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="22 4 12 14.01 9 11.01" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`,
        error: `<svg class="song-status-icon status-error" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke-width="2" stroke-linecap="round"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke-width="2" stroke-linecap="round"/>
        </svg>`,
        skipped: `<svg class="song-status-icon status-skipped" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M5 4l10 8-10 8V4zM19 5v14" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`,
    };
    
    return icons[status] || icons.downloading;
}

function getSongId(songName) {
    return songName.replace(/[^a-zA-Z0-9]/g, '-');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showNotification(message, type = 'info') {
    // Simple console notification for now
    // You can enhance this with a toast notification library
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Optional: Add a visual notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'error' ? '#e74c3c' : type === 'success' ? '#1db954' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideInRight 0.3s ease-out;
        max-width: 300px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);
