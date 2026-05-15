const joinOverlay = document.getElementById('join-overlay');
const joinBtn = document.getElementById('join-btn');

joinBtn.onclick = () => {
    console.log("Join button clicked");
    let cleanedUp = false;
    
    // Ensure the overlay disappears even if audio fails
    const cleanup = () => {
        if (cleanedUp) return;
        cleanedUp = true;
        
        joinOverlay.style.opacity = '0';
        setTimeout(() => {
            joinOverlay.style.display = 'none'; // Use display: none to remove from document flow
            console.log("Overlay hidden and removed from flow");
        }, 1000);
        connect();
    };

    // Unblock audio by playing a silent sound
    const audio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFRm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==');
    audio.play().then(() => {
        console.log("Audio unblocked");
        cleanup();
    }).catch(err => {
        console.warn("Audio initialization failed:", err);
        cleanup();
    });
    
    // Safety timeout to ensure we don't hang on the overlay
    setTimeout(cleanup, 2000);
};

// Remove the automatic connect() call at the bottom later or just let this be the only one

// Map logic
// Initialize
