resetBtn.onclick = () => {
    if (confirm("Are you sure you want to start a new story? This will wipe the current story history, characters, and world state.")) {
        socket.send(jsonMsg("reset_story", {}));
        vnDialogueBox.style.display = "none";
        currentStoryText = "";
        currentChunkEl.innerText = "";
        historyContainer.innerHTML = "";
    }
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

pacingSelector.onchange = () => {
    socket.send(jsonMsg("set_pacing", { pacing: pacingSelector.value }));
};

function renderCharacters() {
    characterListEl.innerHTML = "";
    characters.forEach(char => {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.onclick = () => showCharDetail(char);
        
        const portraitUrl = char.portrait || '/static/placeholder-portrait.png';
        
        // Use relationship data if available
        const rel = char.relationship || { trust: 0, fear: 0, affection: 0 };
        
        // Agency indicators
        const goalHtml = char.current_task ? `<div class="char-task"><strong>Doing:</strong> ${char.current_task}</div>` : "";
        
        const metersHtml = `
            <div class="char-meters">
                <div class="meter-row relationship" title="Trust: ${rel.trust}">🤝 <div class="meter-bar"><div class="meter-fill trust" style="width: ${Math.min(100, Math.max(0, rel.trust * 5 + 50))}%"></div></div></div>
                <div class="meter-row relationship" title="Fear: ${rel.fear}">😨 <div class="meter-bar"><div class="meter-fill fear" style="width: ${Math.min(100, Math.max(0, rel.fear * 5 + 50))}%"></div></div></div>
                <div class="meter-row relationship" title="Affection: ${rel.affection}">❤️ <div class="meter-bar"><div class="meter-fill affection" style="width: ${Math.min(100, Math.max(0, rel.affection * 5 + 50))}%"></div></div></div>
            </div>
        `;

        card.innerHTML = `
            <div class="char-portrait-frame">
                <img class="char-portrait" src="${portraitUrl}">
            </div>
            <div class="char-info">
                <h4>${char.name}</h4>
                <div class="char-role">${char.narrative_role}</div>
                <div class="char-tic"><em>"${char.signature_tic || '...'}"</em></div>
                ${goalHtml}
                ${metersHtml}
            </div>
        `;
        
        characterListEl.appendChild(card);
    });
}

function showCharDetail(char) {
    charDetailContent.innerHTML = renderCharacterDetail(char);
    charModal.style.display = "block";
}

function renderCharacterDetail(char) {
    const rel = char.relationship || { trust: 0, fear: 0, affection: 0 };
    return `
        <div class="char-detail-grid">
            <div class="char-detail-left">
                <img class="char-detail-portrait" src="${char.portrait || '/static/placeholder-portrait.png'}" alt="${char.name}">
                <div class="char-detail-relationship">
                    <h3>Social Standing</h3>
                    <div class="stat-box">🤝 Trust: ${rel.trust}</div>
                    <div class="stat-box">😨 Fear: ${rel.fear}</div>
                    <div class="stat-box">❤️ Affection: ${rel.affection}</div>
                </div>
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

function scrollStory(element = null) {
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return;
    }

    // Fallback for general scrolling
    setTimeout(() => {
        const historyAtBottom = historyContainer.scrollHeight - historyContainer.scrollTop <= historyContainer.clientHeight + 100;
        const vnAtBottom = vnDialogueBox.scrollHeight - vnDialogueBox.scrollTop <= vnDialogueBox.clientHeight + 100;

        if (historyAtBottom) {
            historyContainer.scrollTop = historyContainer.scrollHeight;
        }
        if (vnAtBottom) {
            vnDialogueBox.scrollTop = vnDialogueBox.scrollHeight;
        }
    }, 10);
}

// Input Handlers
inputForm.onsubmit = (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    
    // Clear the current generation box when submitting
    currentStoryText = "";
    currentChunkEl.innerText = "";
    vnDialogueBox.style.display = "none";

    const userBlock = document.createElement('div');
    userBlock.className = 'story-block user-block';
    userBlock.innerText = `> ${text || "Continue..."}`;
    historyContainer.appendChild(userBlock);
    scrollStory(userBlock);

    socket.send(jsonMsg("user_input", text));
    userInput.value = "";
};

continueBtn.onclick = () => {
    // Simulate empty form submission
    inputForm.dispatchEvent(new Event('submit'));
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

