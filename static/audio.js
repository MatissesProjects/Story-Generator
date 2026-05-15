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
        if (isPaused) {
            currentMusic.pause();
        }
        const targetVol = (isDucked ? DUCKED_MUSIC_VOL : NORMAL_MUSIC_VOL) * globalVolume;
        fadeIn(currentMusic, targetVol);
    }).catch(e => console.warn("Music autoplay blocked:", e));
}

function duckAudio() {
    if (isDucked) return;
    isDucked = true;
    if (currentMusic) currentMusic.volume = DUCKED_MUSIC_VOL * globalVolume;
    if (currentAmbiance) currentAmbiance.volume = DUCKED_AMBIANCE_VOL * globalVolume;
}

function unduckAudio() {
    if (!isDucked) return;
    isDucked = false;
    if (currentMusic) currentMusic.volume = NORMAL_MUSIC_VOL * globalVolume;
    if (currentAmbiance) currentAmbiance.volume = NORMAL_AMBIANCE_VOL * globalVolume;
}

function fadeIn(audio, targetVol = 0.5) {
    let vol = 0;
    audio.volume = 0;
    const interval = setInterval(() => {
        vol += 0.02;
        // Adjust targetVol dynamically if globalVolume changed during fade? 
        // For simplicity, we use the targetVol passed at start
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

// Audio Management
function queueAudio(url, speaker, content) {
    // Create a block in the history for this upcoming audio
    const block = document.createElement('div');
    block.className = 'story-block speaker-block';
    block.innerHTML = `<span class="speaker-label">${speaker}:</span> <span class="content-text">${content || "..."}</span>`;
    historyContainer.appendChild(block);
    
    audioQueue.push({ url, speaker, content, element: block });
    if (!isPlaying) {
        playNextAudio();
    }
}

async function playNextAudio() {
    if (audioQueue.length === 0) {
        isPlaying = false;
        unduckAudio();
        // Remove active highlighting from all blocks
        document.querySelectorAll('.story-block.active').forEach(el => el.classList.remove('active'));
        return;
    }

    isPlaying = true;
    duckAudio();
    const { url, speaker, content, element } = audioQueue.shift();
    
    // Highlight the active block in history
    document.querySelectorAll('.story-block.active').forEach(el => el.classList.remove('active'));
    if (element) {
        element.classList.add('active');
        // Populate the content if it was "..."
        const contentEl = element.querySelector('.content-text');
        if (contentEl && content) {
            contentEl.innerText = content;
        }
        scrollStory(element);
    }

    // Apply visual sync if available
    if (visualQueue.length > 0) {
        const nextVisuals = visualQueue.shift();
        updateVisualStack(nextVisuals);
    }
    
    statusIndicator.innerText = `Speaking: ${speaker}...`;
    scrollStory();
    
    currentAudio = new Audio(url);
    currentAudio.volume = globalVolume;
    
    currentAudio.onended = () => {
        currentAudio = null;
        playNextAudio();
    };

    currentAudio.onerror = (e) => {
        console.error("Audio Playback Error:", e);
        currentAudio = null;
        playNextAudio();
    };

    try {
        await currentAudio.play();
        if (isPaused) {
            currentAudio.pause();
        }
    } catch (err) {
        console.warn("Autoplay blocked or playback error:", err);
        playNextAudio();
    }
}

pauseBtn.onclick = () => {
    isPaused = !isPaused;
    pauseBtn.innerText = isPaused ? "Resume Audio" : "Pause Audio";
    pauseBtn.style.backgroundColor = isPaused ? "#facc15" : "";

    if (isPaused) {
        if (currentAudio) currentAudio.pause();
        if (currentMusic) currentMusic.pause();
        if (currentAmbiance) currentAmbiance.pause();
    } else {
        if (currentAudio) currentAudio.play().catch(e => console.warn("Audio resume blocked:", e));
        if (currentMusic) currentMusic.play().catch(e => console.warn("Music resume blocked:", e));
        if (currentAmbiance) currentAmbiance.play().catch(e => console.warn("Ambiance resume blocked:", e));
    }
};

volumeSlider.oninput = (e) => {
    globalVolume = parseFloat(e.target.value);
    
    // Update currently playing speech
    if (currentAudio) currentAudio.volume = globalVolume;
    
    // Update background audio (respecting ducking)
    if (currentMusic) {
        const targetMusicVol = isDucked ? DUCKED_MUSIC_VOL : NORMAL_MUSIC_VOL;
        currentMusic.volume = targetMusicVol * globalVolume;
    }
    if (currentAmbiance) {
        const targetAmbVol = isDucked ? DUCKED_AMBIANCE_VOL : NORMAL_AMBIANCE_VOL;
        currentAmbiance.volume = targetAmbVol * globalVolume;
    }
};

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
        if (isPaused) {
            currentAmbiance.pause();
        }
        fadeIn(currentAmbiance, 0.3 * globalVolume); // Ambiance slightly quieter than music
    }).catch(e => console.warn("Ambiance autoplay blocked:", e));
}

