mapBtn.onclick = () => {
    mapOverlay.style.display = "block";
    socket.send(jsonMsg("get_map", {}));
};

closeMap.onclick = () => {
    mapOverlay.style.display = "none";
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

