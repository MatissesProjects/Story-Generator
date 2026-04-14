const wsUrl = `ws://${window.location.host}/ws`;
let socket;
let currentStoryText = "";
const audioQueue = [];
let isPlaying = false;
let currentMusic = null;
let nextMusic = null;

// DOM Elements
const historyContainer = document.getElementById('history-container');
const currentChunkEl = document.getElementById('current-chunk');
const statusIndicator = document.getElementById('status-indicator');
const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const debugOutput = document.getElementById('debug-output');
const narrativeSeedEl = document.getElementById('narrative-seed');
const plotThreadsEl = document.getElementById('plot-threads');
const characterListEl = document.getElementById('character-list');
const questListEl = document.getElementById('quest-list');
const locationNameEl = document.getElementById('current-location-name');
const backgroundVisualEl = document.getElementById('background-visual');
const sparkBtn = document.getElementById('spark-btn');
const mapBtn = document.getElementById('map-btn');
const mapOverlay = document.getElementById('map-overlay');
const closeMap = document.getElementById('close-map');
const mapCanvas = document.getElementById('map-canvas');
const timelineBtn = document.getElementById('timeline-btn');
const timelineOverlay = document.getElementById('timeline-overlay');
const closeTimeline = document.getElementById('close-timeline');
const timelineContainer = document.getElementById('timeline-container');
const addCharForm = document.getElementById('add-char-form');
const addPlotThreadForm = document.getElementById('add-plot-thread-form');

let characters = [];
let currentPosition = { x: 0, y: 0 };
let currentLocationName = "";

function connect() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        statusIndicator.innerText = "Connected to Story Engine";
        addLog("System", "WebSocket connection established.");
        socket.send(jsonMsg("get_state", {}));
    };

    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleMessage(message);
    };

    socket.onclose = () => {
        statusIndicator.innerText = "Disconnected. Reconnecting...";
        setTimeout(connect, 2000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket Error:", err);
    };
}

// Map logic
mapBtn.onclick = () => {
    mapOverlay.style.display = "block";
    socket.send(jsonMsg("get_map", {}));
};

closeMap.onclick = () => {
    mapOverlay.style.display = "none";
};

window.onclick = (event) => {
    if (event.target == mapOverlay) {
        mapOverlay.style.display = "none";
    }
};

const tileCache = {};

function renderMap(data) {
    const ctx = mapCanvas.getContext('2d');
    const width = mapCanvas.width = mapCanvas.offsetWidth;
    const height = mapCanvas.height = mapCanvas.offsetHeight;
    
    ctx.clearRect(0, 0, width, height);
    
    if (data.locations.length === 0) {
        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.fillText("No locations discovered yet.", width/2, height/2);
        return;
    }

    // Find bounds to center/scale map
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    data.locations.forEach(l => {
        if (l.x < minX) minX = l.x;
        if (l.y < minY) minY = l.y;
        if (l.x > maxX) maxX = l.x;
        if (l.y > maxY) maxY = l.y;
    });

    const padding = 100;
    const mapWidth = (maxX - minX) || 1;
    const mapHeight = (maxY - minY) || 1;
    const scale = Math.min((width - padding*2) / mapWidth, (height - padding*2) / mapHeight, 1);
    
    const centerX = width / 2;
    const centerY = height / 2;
    const offsetX = centerX - ((minX + maxX) / 2) * scale;
    const offsetY = centerY - ((minY + maxY) / 2) * scale;

    // Draw Paths
    ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
    ctx.lineWidth = 3;
    ctx.setLineDash([5, 5]);
    data.paths.forEach(p => {
        const from = data.locations.find(l => l.id === p.from_id);
        const to = data.locations.find(l => l.id === p.to_id);
        if (from && to) {
            ctx.beginPath();
            ctx.moveTo(from.x * scale + offsetX, -from.y * scale + offsetY);
            ctx.lineTo(to.x * scale + offsetX, -to.y * scale + offsetY);
            ctx.stroke();
        }
    });
    ctx.setLineDash([]);

    // Draw Tiles and Locations
    data.locations.forEach(l => {
        const x = l.x * scale + offsetX;
        const y = -l.y * scale + offsetY;
        const tileSize = 80 * scale;

        // Draw Tile if available
        if (l.tile_url) {
            if (!tileCache[l.tile_url]) {
                const img = new Image();
                img.src = l.tile_url;
                img.onload = () => renderMap(data); // Re-render when loaded
                tileCache[l.tile_url] = img;
            }
            if (tileCache[l.tile_url].complete) {
                ctx.save();
                ctx.beginPath();
                ctx.rect(x - tileSize/2, y - tileSize/2, tileSize, tileSize);
                ctx.clip();
                ctx.drawImage(tileCache[l.tile_url], x - tileSize/2, y - tileSize/2, tileSize, tileSize);
                ctx.restore();
                // Border for tile
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                ctx.strokeRect(x - tileSize/2, y - tileSize/2, tileSize, tileSize);
            }
        }
        
        const isCurrent = l.name === currentLocationName;
        
        // Node point
        ctx.fillStyle = isCurrent ? "#4a90e2" : "rgba(255,255,255,0.5)";
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
        
        if (isCurrent) {
            ctx.strokeStyle = "white";
            ctx.lineWidth = 2;
            ctx.stroke();
            // Glow effect
            ctx.shadowBlur = 10;
            ctx.shadowColor = "#4a90e2";
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
        
        ctx.fillStyle = "white";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "center";
        ctx.shadowBlur = 4;
        ctx.shadowColor = "black";
        ctx.fillText(l.name, x, y + tileSize/2 + 15);
        ctx.shadowBlur = 0;
    });
}

// Timeline logic
timelineBtn.onclick = () => {
    timelineOverlay.style.display = "block";
    socket.send(jsonMsg("get_timeline", {}));
};

closeTimeline.onclick = () => {
    timelineOverlay.style.display = "none";
};

function renderTimeline(data) {
    timelineContainer.innerHTML = "";
    data.snapshots.forEach(snap => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.onclick = () => {
            if (confirm(`Checkout Turn ${snap.turn_number}? This will reset the story to this point.`)) {
                socket.send(jsonMsg("checkout_snapshot", { snapshot_id: snap.id }));
                timelineOverlay.style.display = "none";
            }
        };

        item.innerHTML = `
            <div class="timeline-header">
                <span>Turn #${snap.turn_number}</span>
                <span>${new Date(snap.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="timeline-content">
                <div class="timeline-player">P: ${snap.user_input || "(Continuation)"}</div>
                <div>S: ${snap.assistant_response.substring(0, 100)}...</div>
            </div>
        `;
        timelineContainer.appendChild(item);
    });
}

function handleMessage(message) {
    switch (message.type) {
        case 'story_chunk':
            currentStoryText += message.content;
            currentChunkEl.innerText = currentStoryText;
            scrollStory();
            break;
        
        case 'audio_event':
            const audioUrl = `${window.location.protocol}//${window.location.host}${message.url}`;
            queueAudio(audioUrl, message.speaker);
            break;

        case 'debug':
            addLog("Debug", message.content);
            break;

        case 'info':
            addLog("Info", message.content);
            break;

        case 'map_data':
            renderMap(message);
            break;

        case 'timeline_data':
            renderTimeline(message);
            break;

        case 'state_update_request':
            socket.send(jsonMsg("get_state", {}));
            // Clear current chat history visually to show we've switched
            historyContainer.innerHTML = "<em>Narrative checkout complete. Current state loaded.</em>";
            currentStoryText = "";
            currentChunkEl.innerText = "";
            break;

        case 'spark':
            addLog("Spark", message.content);
            const sparkBlock = document.createElement('div');
            sparkBlock.className = 'story-block spark-block';
            sparkBlock.innerHTML = `<strong>Spark Idea:</strong> ${message.content}`;
            historyContainer.appendChild(sparkBlock);
            scrollStory();
            break;

        case 'validation_failure':
            addLog("Logic", `Action blocked: ${message.content}`);
            const failBlock = document.createElement('div');
            failBlock.className = 'story-block validation-failure';
            failBlock.style.color = '#ff6b6b';
            failBlock.innerText = `[Logic Error]: ${message.content}`;
            historyContainer.appendChild(failBlock);
            scrollStory();
            break;

        case 'state_update':
            if (message.seed) {
                narrativeSeedEl.innerText = message.seed;
            }
            if (message.threads) {
                plotThreadsEl.innerHTML = "";
                message.threads.forEach(t => {
                    const li = document.createElement('li');
                    li.innerText = t;
                    plotThreadsEl.appendChild(li);
                });
            }
            if (message.characters) {
                characters = message.characters;
                renderCharacters();
            }
            if (message.quests) {
                renderQuests(message.quests);
            }
            if (message.location) {
                locationNameEl.innerText = currentLocationName = message.location;
            }
            if (message.location_image) {
                backgroundVisualEl.style.backgroundImage = `url('${message.location_image}')`;
            }
            break;

        case 'portrait_update':
            const char = characters.find(c => c.name === message.name);
            if (char) {
                char.portrait = message.url;
            } else {
                characters.push({ name: message.name, portrait: message.url });
            }
            renderCharacters();
            break;

        case 'scene_update':
            addLog("Scene", `Entered: ${message.location}`);
            locationNameEl.innerText = currentLocationName = message.location;
            if (message.url) {
                backgroundVisualEl.style.backgroundImage = `url('${message.url}')`;
            }
            break;

        case 'music_event':
            addLog("Music", `Mood: ${message.mood} - Playing: ${message.filename}`);
            updateMusic(message.url);
            break;
    }
}

function updateMusic(url) {
    if (currentMusic && currentMusic.src.includes(url)) return;

    const newAudio = new Audio(url);
    newAudio.loop = true;
    newAudio.volume = 0;
    
    if (currentMusic) {
        fadeOut(currentMusic);
    }

    currentMusic = newAudio;
    currentMusic.play().then(() => {
        fadeIn(currentMusic);
    }).catch(e => console.warn("Music autoplay blocked:", e));
}

function fadeIn(audio) {
    let vol = 0;
    const interval = setInterval(() => {
        vol += 0.05;
        if (vol >= 0.5) {
            audio.volume = 0.5;
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 200);
}

function fadeOut(audio) {
    let vol = audio.volume;
    const interval = setInterval(() => {
        vol -= 0.05;
        if (vol <= 0) {
            audio.pause();
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 200);
}

function renderCharacters() {
    characterListEl.innerHTML = "";
    characters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'char-card';
        
        const img = document.createElement('img');
        img.className = 'char-portrait';
        img.src = char.portrait || '/static/placeholder-portrait.png'; // Fallback
        
        const info = document.createElement('div');
        info.className = 'char-info';
        info.innerHTML = `<h4>${char.name}</h4><p>${char.traits}</p>`;
        
        card.appendChild(img);
        card.appendChild(info);
        characterListEl.appendChild(card);
    });
}

function renderQuests(quests) {
    questListEl.innerHTML = "";
    quests.forEach(quest => {
        const item = document.createElement('div');
        item.className = 'quest-item';
        
        const objectivesHtml = quest.objectives.map(o => `<li>${o.description}</li>`).join("");
        
        item.innerHTML = `
            <h4>${quest.title}</h4>
            <p>${quest.description}</p>
            <ul class="quest-objectives">
                ${objectivesHtml}
            </ul>
        `;
        questListEl.appendChild(item);
    });
}

    // End of stream detection (this is heuristic based on the current server logic)
    // In a real app, the server would send a 'stream_end' message.
}

function addLog(type, content) {
    const entry = document.createElement('div');
    entry.className = 'debug-entry';
    entry.innerHTML = `<strong>${type}:</strong> ${content}`;
    debugOutput.prepend(entry);
}

function scrollStory() {
    historyContainer.scrollTop = historyContainer.scrollHeight;
}

// Audio Management
function queueAudio(url, speaker) {
    audioQueue.push({ url, speaker });
    if (!isPlaying) {
        playNextAudio();
    }
}

async function playNextAudio() {
    if (audioQueue.length === 0) {
        isPlaying = false;
        return;
    }

    isPlaying = true;
    const { url, speaker } = audioQueue.shift();
    
    statusIndicator.innerText = `Speaking: ${speaker}...`;
    const audio = new Audio(url);
    
    audio.onended = () => {
        playNextAudio();
    };

    audio.onerror = (e) => {
        console.error("Audio Playback Error:", e);
        playNextAudio();
    };

    try {
        await audio.play();
    } catch (err) {
        console.warn("Autoplay blocked or playback error:", err);
        // Play next anyway
        playNextAudio();
    }
}

// Input Handlers
inputForm.onsubmit = (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Move current text to history
    if (currentStoryText) {
        const block = document.createElement('div');
        block.className = 'story-block';
        block.innerText = currentStoryText;
        historyContainer.appendChild(block);
        currentStoryText = "";
        currentChunkEl.innerText = "";
    }

    const userBlock = document.createElement('div');
    userBlock.className = 'story-block user-block';
    userBlock.innerText = `> ${text}`;
    historyContainer.appendChild(userBlock);

    socket.send(jsonMsg("user_input", text));
    userInput.value = "";
    scrollStory();
};

sparkBtn.onclick = () => {
    socket.send(jsonMsg("user_input", "spark"));
};

addCharForm.onsubmit = (e) => {
    e.preventDefault();
    const content = {
        name: document.getElementById('char-name').value,
        traits: document.getElementById('char-traits').value,
        description: document.getElementById('char-desc').value
    };
    socket.send(jsonMsg("add_character", content));
    addCharForm.reset();
};

addPlotThreadForm.onsubmit = (e) => {
    e.preventDefault();
    const desc = document.getElementById('plot-thread-input').value;
    socket.send(jsonMsg("add_plot_thread", { description: desc }));
    
    // Optimistically add to list
    const li = document.createElement('li');
    li.innerText = desc;
    plotThreadsEl.appendChild(li);
    addPlotThreadForm.reset();
};

function jsonMsg(type, content) {
    return JSON.stringify({ type, content });
}

// Initialize
connect();
