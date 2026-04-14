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
const locationNameEl = document.getElementById('current-location-name');
const backgroundVisualEl = document.getElementById('background-visual');
const sparkBtn = document.getElementById('spark-btn');
const addCharForm = document.getElementById('add-char-form');
const addPlotThreadForm = document.getElementById('add-plot-thread-form');

let characters = [];

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
            // Check for narrative seed in debug or specific type
            if (message.content.includes("Seed: true")) {
                // If the seed changed, we might want to update it, but usually it's pushed as 'info'
            }
            break;

        case 'info':
            addLog("Info", message.content);
            if (message.content.includes("Narrative summary updated")) {
                // Request state update or wait for next turn to see seed in debug
            }
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
            if (message.location) {
                locationNameEl.innerText = message.location;
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
            locationNameEl.innerText = message.location;
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
