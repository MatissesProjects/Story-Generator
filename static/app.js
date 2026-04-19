const wsUrl = `ws://${window.location.host}/ws`;
let socket;
let currentStoryText = "";
const audioQueue = [];
const visualQueue = [];
let isPlaying = false;
let currentMusic = null;
let currentAmbiance = null;
let nextMusic = null;
let lastNonLeitmotifUrl = null;

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
const socialListEl = document.getElementById('social-list');
const pacingSelector = document.getElementById('pacing-selector');
const arcDisplayEl = document.getElementById('arc-display');
const milestoneDisplayEl = document.getElementById('milestone-display');
const inventoryListEl = document.getElementById('inventory-list');
const statsListEl = document.getElementById('stats-list');
const locationNameEl = document.getElementById('current-location-name');
const backgroundVisualEl = document.getElementById('background-visual');
const resetBtn = document.getElementById('reset-btn');
const sparkBtn = document.getElementById('spark-btn');
const mapBtn = document.getElementById('map-btn');
const mapOverlay = document.getElementById('map-overlay');
const closeMap = document.getElementById('close-map');
const mapCanvas = document.getElementById('map-canvas');
const timelineBtn = document.getElementById('timeline-btn');
const timelineOverlay = document.getElementById('timeline-overlay');
const closeTimeline = document.getElementById('close-timeline');
const charModal = document.getElementById('char-modal');
const closeChar = document.getElementById('close-char');
const charDetailContent = document.getElementById('char-detail-content');
const timelineContainer = document.getElementById('timeline-container');
const addCharForm = document.getElementById('add-char-form');
const addPlotThreadForm = document.getElementById('add-plot-thread-form');

let characters = [];
let currentPosition = { x: 0, y: 0 };
let currentLocationName = "";

// Audio Ducking state
let isDucked = false;
const NORMAL_MUSIC_VOL = 0.5;
const NORMAL_AMBIANCE_VOL = 0.3;
const DUCKED_MUSIC_VOL = 0.15;
const DUCKED_AMBIANCE_VOL = 0.1;

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
resetBtn.onclick = () => {
    if (confirm("Are you sure you want to start a new story? This will wipe the current story history, characters, and world state.")) {
        socket.send(jsonMsg("reset_story", {}));
        vnDialogueBox.style.display = "none";
        currentStoryText = "";
        currentChunkEl.innerText = "";
        historyContainer.innerHTML = "";
    }
};

mapBtn.onclick = () => {
    mapOverlay.style.display = "block";
    socket.send(jsonMsg("get_map", {}));
};

closeMap.onclick = () => {
    mapOverlay.style.display = "none";
};

closeChar.onclick = () => {
    charModal.style.display = "none";
};

window.onclick = (event) => {
    if (event.target == mapOverlay) {
        mapOverlay.style.display = "none";
    }
    if (event.target == charModal) {
        charModal.style.display = "none";
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
                vnDialogueBox.style.display = "none";
                vnNameTag.innerText = "Narrator";
                currentStoryText = "";
                currentChunkEl.innerText = "";
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

pacingSelector.onchange = () => {
    socket.send(jsonMsg("set_pacing", { pacing: pacingSelector.value }));
};

const vnDialogueBox = document.getElementById('vn-dialogue-box');
const vnNameTag = document.getElementById('vn-name-tag');

function handleMessage(message) {
    switch (message.type) {
        case 'story_chunk':
            currentStoryText += message.content;
            currentChunkEl.innerText = currentStoryText;
            vnDialogueBox.style.display = "block";
            scrollStory();
            break;
        
        case 'audio_event':
            const audioUrl = `${window.location.protocol}//${window.location.host}${message.url}`;
            
            // Move current text to history before starting new speaker block
            if (currentStoryText) {
                const block = document.createElement('div');
                block.className = 'story-block';
                block.innerText = currentStoryText;
                historyContainer.appendChild(block);
                currentStoryText = "";
                currentChunkEl.innerText = "";
            }
            
            vnNameTag.innerText = message.speaker;
            vnDialogueBox.style.display = "block";
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
            historyContainer.innerHTML = "<em>Narrative switch complete.</em>";
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
            if (message.relationships) {
                renderSocialStanding(message.relationships);
            }
            if (message.inventory) {
                renderInventory(message.inventory);
            }
            if (message.stats) {
                renderStats(message.stats);
            }
            if (message.location) {
                locationNameEl.innerText = currentLocationName = message.location;
            }
            if (message.location_image) {
                backgroundVisualEl.style.backgroundImage = `url('${message.location_image}')`;
            }
            if (message.pacing) {
                pacingSelector.value = message.pacing;
            }
            renderArc(message.active_arc, message.milestone_index);
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
                toggleKenBurns(backgroundVisualEl);
            }
            break;

        case 'music_event':
            addLog("Music", `Mood: ${message.mood} - Playing: ${message.filename}`);
            updateMusic(message.url, message.is_leitmotif);
            break;

        case 'visual_update':
            // Queue visuals to sync with audio segments
            visualQueue.push(message.content);
            
            // Preload visuals to trigger server-side generation early
            preloadVisuals(message.content);

            // If nothing is playing, apply immediately
            if (!isPlaying) {
                updateVisualStack(message.content);
            }
            break;

        case 'atmosphere_update':
            const atmos = message.content;
            addLog("Environment", `Lighting: ${atmos.lighting}, Weather: ${atmos.weather}`);
            applyAtmosphere(atmos);
            break;

        case 'ambiance_event':
            addLog("Ambiance", "Changing background ambiance...");
            updateAmbiance(message.url);
            break;

        case 'progress':
            statusIndicator.innerText = message.content;
            if (message.level === 'success') {
                statusIndicator.style.color = '#4ade80';
                setTimeout(() => {
                    statusIndicator.style.color = '';
                    statusIndicator.innerText = "Connected to Story Engine";
                }, 3000);
            } else {
                statusIndicator.style.color = '#facc15'; // yellow/amber for progress
            }
            addLog("Progress", message.content);
            break;
    }
}

function updateMusic(url, isLeitmotif = false) {
    if (currentMusic && currentMusic.src.includes(url)) return;

    if (!isLeitmotif) {
        lastNonLeitmotifUrl = url;
    }

    const newAudio = new Audio(url);
    newAudio.loop = true;
    newAudio.volume = 0;

    if (currentMusic) {
        fadeOut(currentMusic);
    }

    currentMusic = newAudio;
    currentMusic.play().then(() => {
        const targetVol = isDucked ? DUCKED_MUSIC_VOL : NORMAL_MUSIC_VOL;
        fadeIn(currentMusic, targetVol);
    }).catch(e => console.warn("Music autoplay blocked:", e));
}

function duckAudio() {
    if (isDucked) return;
    isDucked = true;
    if (currentMusic) currentMusic.volume = DUCKED_MUSIC_VOL;
    if (currentAmbiance) currentAmbiance.volume = DUCKED_AMBIANCE_VOL;
}

function unduckAudio() {
    if (!isDucked) return;
    isDucked = false;
    if (currentMusic) currentMusic.volume = NORMAL_MUSIC_VOL;
    if (currentAmbiance) currentAmbiance.volume = NORMAL_AMBIANCE_VOL;
}

function toggleKenBurns(el) {
    el.classList.remove('ken-burns-in', 'ken-burns-out');
    // Force reflow to restart animation
    void el.offsetWidth;
    const effect = Math.random() > 0.5 ? 'ken-burns-in' : 'ken-burns-out';
    el.classList.add(effect);
}

function fadeIn(audio, targetVol = 0.5) {
    let vol = 0;
    audio.volume = 0;
    const interval = setInterval(() => {
        vol += 0.02;
        if (vol >= targetVol) {
            audio.volume = targetVol;
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 100);
}

function fadeOut(audio) {
    let vol = audio.volume;
    const interval = setInterval(() => {
        vol -= 0.02;
        if (vol <= 0) {
            audio.volume = 0;
            audio.pause();
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 100);
}

function renderCharacters() {
    characterListEl.innerHTML = "";
    characters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.onclick = () => showCharDetail(char);
        
        const img = document.createElement('img');
        img.className = 'char-portrait';
        img.src = char.portrait || '/static/placeholder-portrait.png'; 
        
        const info = document.createElement('div');
        info.className = 'char-info';
        
        // Agency indicators
        const goalHtml = char.current_task ? `<div class="char-task"><strong>Current Activity:</strong> ${char.current_task}</div>` : "";
        
        const metersHtml = `
            <div class="char-meters">
                <div class="meter-row" title="Social">🤝 <div class="meter-bar"><div class="meter-fill" style="width: ${char.social}%"></div></div></div>
                <div class="meter-row" title="Ambition">🏆 <div class="meter-bar"><div class="meter-fill" style="width: ${char.ambition}%"></div></div></div>
                <div class="meter-row" title="Safety">🛡️ <div class="meter-bar"><div class="meter-fill" style="width: ${char.safety}%"></div></div></div>
                <div class="meter-row" title="Resources">💰 <div class="meter-bar"><div class="meter-fill" style="width: ${char.resources}%"></div></div></div>
            </div>
        `;

        info.innerHTML = `
            <h4>${char.name} <small>(${char.narrative_role})</small></h4>
            <p>${char.traits}</p>
            <div class="char-tic"><em>"${char.signature_tic || '...'}"</em></div>
            ${goalHtml}
            ${metersHtml}
        `;
        
        card.appendChild(img);
        card.appendChild(info);
        characterListEl.appendChild(card);
    });
}

function showCharDetail(char) {
    charDetailContent.innerHTML = renderCharacterDetail(char);
    charModal.style.display = "block";
}

function renderCharacterDetail(char) {
    return `
        <div class="char-detail-grid">
            <div class="char-detail-left">
                <img class="char-detail-portrait" src="${char.portrait || '/static/placeholder-portrait.png'}" alt="${char.name}">
            </div>
            <div class="char-detail-info">
                <h2>${char.name} <small>(${char.narrative_role})</small></h2>
                <p class="char-detail-traits"><strong>Traits:</strong> ${char.traits}</p>
                <div class="char-detail-bio">
                    <h3>Description</h3>
                    <p>${char.description}</p>
                </div>
                <div class="char-detail-bio">
                    <h3>Signature Tic</h3>
                    <p><em>"${char.signature_tic || 'None identified yet.'}"</em></p>
                </div>
                <div class="char-detail-stats">
                    <div class="stat-box">
                        <label>Social</label>
                        <div class="meter-bar"><div class="meter-fill" style="width: ${char.social}%"></div></div>
                        <span>${char.social}/100</span>
                    </div>
                    <div class="stat-box">
                        <label>Ambition</label>
                        <div class="meter-bar"><div class="meter-fill" style="width: ${char.ambition}%"></div></div>
                        <span>${char.ambition}/100</span>
                    </div>
                    <div class="stat-box">
                        <label>Safety</label>
                        <div class="meter-bar"><div class="meter-fill" style="width: ${char.safety}%"></div></div>
                        <span>${char.safety}/100</span>
                    </div>
                    <div class="stat-box">
                        <label>Resources</label>
                        <div class="meter-bar"><div class="meter-fill" style="width: ${char.resources}%"></div></div>
                        <span>${char.resources}/100</span>
                    </div>
                </div>
                <div class="char-detail-bio" style="margin-top: 1.5rem;">
                    <h3>Current Status</h3>
                    <p><strong>Goal:</strong> ${char.current_goal || 'Searching for purpose...'}</p>
                    <p><strong>Task:</strong> ${char.current_task || 'Idle'}</p>
                </div>
            </div>
        </div>
    `;
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

function renderSocialStanding(relationships) {
    socialListEl.innerHTML = "";
    relationships.forEach(rel => {
        const item = document.createElement('div');
        item.className = 'social-item';
        item.innerHTML = `
            <h4>${rel.other_name}</h4>
            <div class="social-stats">
                <span>🤝 <span class="stat-val">${rel.trust}</span></span>
                <span>😨 <span class="stat-val">${rel.fear}</span></span>
                <span>❤️ <span class="stat-val">${rel.affection}</span></span>
            </div>
        `;
        socialListEl.appendChild(item);
    });
}

function renderArc(arc, milestoneIdx) {
    if (!arc) {
        arcDisplayEl.innerText = "No active arc.";
        milestoneDisplayEl.innerHTML = "";
        return;
    }

    arcDisplayEl.innerText = arc.title;
    
    if (milestoneIdx >= 0 && milestoneIdx < arc.milestones.length) {
        const m = arc.milestones[milestoneIdx];
        milestoneDisplayEl.innerHTML = `
            <span class="milestone-name">Chapter ${milestoneIdx + 1}: ${m.name}</span>
            <span class="milestone-desc">${m.description}</span>
        `;
    } else if (milestoneIdx >= arc.milestones.length) {
        milestoneDisplayEl.innerHTML = "<strong>Adventure Arc Completed!</strong>";
    }
}

function renderInventory(items) {
    inventoryListEl.innerHTML = items.length === 0 ? "Empty" : "";
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'inventory-item';
        div.title = item.description;
        div.innerText = `${item.item_name} x${item.quantity}`;
        inventoryListEl.appendChild(div);
    });
}

function renderStats(stats) {
    statsListEl.innerHTML = stats.length === 0 ? "No stats" : "";
    stats.forEach(s => {
        const div = document.createElement('div');
        div.className = 'stat-item';
        div.innerHTML = `<span class="stat-label">${s.stat_name}:</span> ${s.stat_value}`;
        statsListEl.appendChild(div);
    });
}
    // End of stream detection (this is heuristic based on the current server logic)
    // In a real app, the server would send a 'stream_end' message.

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
        unduckAudio();
        return;
    }

    isPlaying = true;
    duckAudio();
    const { url, speaker } = audioQueue.shift();
    
    // Apply visual sync if available
    if (visualQueue.length > 0) {
        const nextVisuals = visualQueue.shift();
        updateVisualStack(nextVisuals);
    }
    
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

function applyAtmosphere(atmos) {
    const overlay = document.getElementById('atmosphere-overlay');
    if (!overlay) return;

    // Apply Tint
    overlay.style.backgroundColor = atmos.tint || 'rgba(0,0,0,0)';

    // Mood-based UI styling
    const mood = (atmos.lighting || "").toLowerCase();
    vnDialogueBox.classList.remove('mood-tension', 'mood-combat', 'mood-mystical', 'mood-mournful');
    
    if (mood.includes('tension') || mood.includes('yellow')) vnDialogueBox.classList.add('mood-tension');
    else if (mood.includes('combat') || mood.includes('red')) vnDialogueBox.classList.add('mood-combat');
    else if (mood.includes('purple') || mood.includes('mystic')) vnDialogueBox.classList.add('mood-mystical');
    else if (mood.includes('blue') || mood.includes('mourn')) vnDialogueBox.classList.add('mood-mournful');

    // Apply Haptic (Screen Shake)
    const haptic = (atmos.haptic || "").toLowerCase();
    if (haptic.includes('rumble') || haptic.includes('pulse') || haptic.includes('shake')) {
        document.body.classList.add('shake');
        setTimeout(() => {
            document.body.classList.remove('shake');
        }, 800);
    }

    // Visual Beats (Glitches)
    const visualStack = document.getElementById('visual-stack');
    if (haptic.includes('glitch') || haptic.includes('anomaly')) {
        visualStack.classList.add('glitch-active');
        setTimeout(() => visualStack.classList.remove('glitch-active'), 500);
    }

    // Apply Visual Punctuation (Flash Red)
    if (haptic.includes('damage') || haptic.includes('impact') || (atmos.lighting && atmos.lighting.toLowerCase().includes('red'))) {
        overlay.classList.add('flash-red');
        setTimeout(() => {
            overlay.classList.remove('flash-red');
        }, 800);
    }
}

function preloadVisuals(stack) {
    if (!stack) return;
    
    // Warm up environment
    if (stack.environment) {
        new Image().src = stack.environment;
    }
    
    // Warm up character slots
    if (stack.slots) {
        Object.values(stack.slots).forEach(url => {
            if (url) new Image().src = url;
        });
    }
}

function updateVisualStack(stack) {
    console.log("Visual: Updating stack:", stack);
    const layers = {
        'texture': document.getElementById('layer-texture'),
        'environment': document.getElementById('layer-environment'),
        'overlay': document.getElementById('layer-overlay')
    };

    const slots = {
        'left': document.getElementById('slot-left'),
        'center': document.getElementById('slot-center'),
        'right': document.getElementById('slot-right')
    };

    const isNarrator = stack.primary === "Narrator";

    // Update static layers
    for (const [key, el] of Object.entries(layers)) {
        const url = stack[key];
        if (url) {
            el.style.backgroundImage = `url('${url}')`;
            
            // Base opacity
            let opacity = 1.0;
            if (key === 'texture') opacity = 0.4;
            if (key === 'overlay') opacity = 0.3;
            
            if (!isNarrator && key === 'environment') opacity = 0.5; // Dim env more when someone is talking

            el.style.opacity = opacity;
            
            if (key === 'environment') {
                toggleKenBurns(el);
            }
        } else {
            el.style.opacity = 0;
        }
    }

    // Update character slots
    for (const [key, el] of Object.entries(slots)) {
        const url = stack.slots[key];
        if (url) {
            el.style.backgroundImage = `url('${url}')`;
            el.classList.add('active');
            
            // Check if this slot contains the primary speaker
            // URL is /asset/portrait/{safename}
            const primarySafe = stack.primary ? stack.primary.toLowerCase().replace(' ', '') : "";
            if (primarySafe && url.includes(primarySafe)) {
                el.classList.add('speaking');
                el.classList.remove('dimmed');
                toggleKenBurns(el); // Focus on the speaker
            } else {
                el.classList.remove('speaking');
                el.classList.add('dimmed');
                el.classList.remove('ken-burns-in', 'ken-burns-out');
            }
        } else {
            el.style.backgroundImage = 'none';
            el.classList.remove('active', 'speaking', 'dimmed', 'ken-burns-in', 'ken-burns-out');
        }
    }
}

function updateAmbiance(url) {
    if (currentAmbiance && currentAmbiance.src.includes(url)) return;

    const newAudio = new Audio(url);
    newAudio.loop = true;
    newAudio.volume = 0;
    
    if (currentAmbiance) {
        fadeOut(currentAmbiance);
    }

    currentAmbiance = newAudio;
    currentAmbiance.play().then(() => {
        fadeIn(currentAmbiance, 0.3); // Ambiance slightly quieter than music
    }).catch(e => console.warn("Ambiance autoplay blocked:", e));
}

function fadeIn(audio, targetVol = 0.5) {
    let vol = 0;
    const interval = setInterval(() => {
        vol += 0.02;
        if (vol >= targetVol) {
            audio.volume = targetVol;
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 100);
}

function fadeOut(audio) {
    let vol = audio.volume;
    const interval = setInterval(() => {
        vol -= 0.02;
        if (vol <= 0) {
            audio.pause();
            clearInterval(interval);
        } else {
            audio.volume = vol;
        }
    }, 100);
}

function jsonMsg(type, content) {
    return JSON.stringify({ type, content });
}

// Initialize
connect();
