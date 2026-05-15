function connect() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        statusIndicator.innerText = "Connected to Story Engine";
        addLog("System", "WebSocket connection established.");
        
        // Send handshake to announce capabilities
        socket.send(jsonMsg("handshake", {
            "gpu": "Local Browser",
            "can_offload_vision": false
        }));
        
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
            vnDialogueBox.style.display = "block";
            
            // Smart scroll for dialogue box: only scroll if user is already at the bottom
            const isAtBottom = vnDialogueBox.scrollHeight - vnDialogueBox.scrollTop <= vnDialogueBox.clientHeight + 60;
            if (isAtBottom) {
                vnDialogueBox.scrollTop = vnDialogueBox.scrollHeight;
            }
            break;
        
        case 'audio_event':
            const audioUrl = `${window.location.protocol}//${window.location.host}${message.url}`;
            
            // Every time a new audio event comes in, it means a speaker block is starting.
            // We clear the current text because the audio event carries the 'definitive' text for this block.
            currentStoryText = "";
            currentChunkEl.innerText = "";
            vnDialogueBox.style.display = "none";
            
            queueAudio(audioUrl, message.speaker, message.content);
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
            currentStoryText = "";
            vnNameTag.innerText = "Narrator";
            vnDialogueBox.style.display = "block";
            addLog("Spark", message.content);
            const sparkBlock = document.createElement('div');
            sparkBlock.className = 'story-block spark-block';
            sparkBlock.innerHTML = `<strong>Spark Idea:</strong> ${message.content}`;
            historyContainer.appendChild(sparkBlock);
            scrollStory(true);
            break;

        case 'validation_failure':
            addLog("Logic", `Action blocked: ${message.content}`);
            const failBlock = document.createElement('div');
            failBlock.className = 'story-block validation-failure';
            failBlock.style.color = '#ff6b6b';
            failBlock.innerText = `[Logic Error]: ${message.content}`;
            historyContainer.appendChild(failBlock);
            scrollStory(true);
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
                const envLayer = document.getElementById('layer-environment');
                if (envLayer) {
                    envLayer.style.backgroundImage = `url('${message.location_image}')`;
                }
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
                const envLayer = document.getElementById('layer-environment');
                if (envLayer) {
                    envLayer.style.backgroundImage = `url('${message.url}')`;
                    toggleKenBurns(envLayer);
                }
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

function jsonMsg(type, content) {
    return JSON.stringify({ type, content });
}

