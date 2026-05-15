import re

def split_app_js():
    with open('static/app.js', 'r') as f:
        lines = f.readlines()

    blocks = {
        'globals': [],
        'network': [],
        'map': [],
        'timeline': [],
        'ui': [],
        'visuals': [],
        'audio': [],
        'main': []
    }
    
    current_block = 'globals'
    
    for i, line in enumerate(lines):
        # Determine boundaries
        if line.startswith('// Audio Ducking state'):
            current_block = 'globals' # still globals
        elif line.startswith('function connect()'):
            current_block = 'network'
        elif line.startswith('const joinOverlay ='):
            current_block = 'main' # Let's put initialization in main
        elif line.startswith('resetBtn.onclick ='):
            current_block = 'ui'
        elif line.startswith('mapBtn.onclick ='):
            current_block = 'map'
        elif line.startswith('closeChar.onclick ='):
            current_block = 'ui'
        elif line.startswith('window.onclick ='):
            current_block = 'ui'
        elif line.startswith('const tileCache ='):
            current_block = 'map'
        elif line.startswith('// Timeline logic'):
            current_block = 'timeline'
        elif line.startswith('pacingSelector.onchange ='):
            current_block = 'ui'
        elif line.startswith('const vnDialogueBox ='):
            current_block = 'globals'
        elif line.startswith('function handleMessage'):
            current_block = 'network'
        elif line.startswith('function updateMusic'):
            current_block = 'audio'
        elif line.startswith('function duckAudio'):
            current_block = 'audio'
        elif line.startswith('function toggleKenBurns'):
            current_block = 'visuals'
        elif line.startswith('function fadeIn'):
            current_block = 'audio'
        elif line.startswith('function fadeOut'):
            current_block = 'audio'
        elif line.startswith('function renderCharacters'):
            current_block = 'ui'
        elif line.startswith('function showCharDetail'):
            current_block = 'ui'
        elif line.startswith('function renderCharacterDetail'):
            current_block = 'ui'
        elif line.startswith('function renderQuests'):
            current_block = 'ui'
        elif line.startswith('function renderArc'):
            current_block = 'ui'
        elif line.startswith('function renderInventory'):
            current_block = 'ui'
        elif line.startswith('function renderStats'):
            current_block = 'ui'
        elif line.startswith('function addLog'):
            current_block = 'ui'
        elif line.startswith('function scrollStory'):
            current_block = 'ui'
        elif line.startswith('// Audio Management'):
            current_block = 'audio'
        elif line.startswith('// Input Handlers'):
            current_block = 'ui'
        elif line.startswith('pauseBtn.onclick ='):
            current_block = 'audio' # Audio specific UI
        elif line.startswith('volumeSlider.oninput ='):
            current_block = 'audio'
        elif line.startswith('inputForm.onsubmit ='):
            current_block = 'ui'
        elif line.startswith('continueBtn.onclick ='):
            current_block = 'ui'
        elif line.startswith('sparkBtn.onclick ='):
            current_block = 'ui'
        elif line.startswith('addCharForm.onsubmit ='):
            current_block = 'ui'
        elif line.startswith('addPlotThreadForm.onsubmit ='):
            current_block = 'ui'
        elif line.startswith('function triggerVisualEffect'):
            current_block = 'visuals'
        elif line.startswith('function createEmber'):
            current_block = 'visuals'
        elif line.startswith('function applyAtmosphere'):
            current_block = 'visuals'
        elif line.startswith('function preloadVisuals'):
            current_block = 'visuals'
        elif line.startswith('function updateVisualStack'):
            current_block = 'visuals'
        elif line.startswith('function updateAmbiance'):
            current_block = 'audio'
        elif line.startswith('function jsonMsg'):
            current_block = 'network'
        elif line.startswith('// Initialize'):
            current_block = 'main'

        blocks[current_block].append(line)

    for name, content in blocks.items():
        with open(f'static/{name}.js', 'w') as f:
            f.writelines(content)
            
    print("Files created.")

split_app_js()
