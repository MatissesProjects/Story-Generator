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

