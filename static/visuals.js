function toggleKenBurns(el) {
    el.classList.remove('ken-burns-in', 'ken-burns-out');
    // Force reflow to restart animation
    void el.offsetWidth;
    const effect = Math.random() > 0.5 ? 'ken-burns-in' : 'ken-burns-out';
    el.classList.add(effect);
}

function triggerVisualEffect(type) {
    const effectsLayer = document.getElementById('effects-layer');
    if (!effectsLayer) return;

    if (type === 'fog') {
        if (!document.querySelector('.effect-fog')) {
            const fog = document.createElement('div');
            fog.className = 'effect-fog';
            effectsLayer.appendChild(fog);
        }
    } else if (type === 'streak') {
        const streak = document.createElement('div');
        streak.className = 'effect-streak';
        streak.style.left = Math.random() * 80 + 10 + '%';
        streak.style.top = Math.random() * 20 + '%';
        effectsLayer.appendChild(streak);
        setTimeout(() => streak.remove(), 1000);
    } else if (type === 'pulse') {
        const pulse = document.createElement('div');
        pulse.className = 'effect-pulse';
        effectsLayer.appendChild(pulse);
        setTimeout(() => pulse.remove(), 2000);
    } else if (type === 'embers') {
        if (!document.querySelector('.effect-ember')) {
            for (let i = 0; i < 20; i++) {
                createEmber(effectsLayer);
            }
        }
    } else if (type === 'clear') {
        effectsLayer.innerHTML = "";
    }
}

function createEmber(parent) {
    const ember = document.createElement('div');
    ember.className = 'effect-ember';
    ember.style.left = Math.random() * 100 + '%';
    ember.style.top = Math.random() * 100 + '%';
    ember.style.setProperty('--dx', (Math.random() * 200 - 100) + 'px');
    ember.style.setProperty('--dy', (Math.random() * -200 - 50) + 'px');
    ember.style.animationDelay = Math.random() * 5 + 's';
    parent.appendChild(ember);
}

function applyAtmosphere(atmos) {
    const overlay = document.getElementById('atmosphere-overlay');
    const effectsLayer = document.getElementById('effects-layer');
    if (!overlay || !effectsLayer) return;

    // Apply Tint with safety check
    let tint = atmos.tint || 'rgba(0,0,0,0)';
    if (!tint.includes('rgba')) {
        tint = tint.replace('rgb', 'rgba').replace(')', ', 0.15)');
    }
    overlay.style.backgroundColor = tint;

    // Apply Visual Effects
    if (atmos.visual_effect) {
        triggerVisualEffect(atmos.visual_effect);
    }

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
    addLog("Visual", `Updating stack: ${JSON.stringify(stack)}`);
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

