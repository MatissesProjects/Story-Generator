const wsUrl = `ws://${window.location.host}/ws`;
let socket;
let currentStoryText = "";
const audioQueue = [];
const visualQueue = [];
let isPlaying = false;
let isPaused = false;
let currentAudio = null;
let currentMusic = null;
let currentAmbiance = null;
let nextMusic = null;
let lastNonLeitmotifUrl = null;
let globalVolume = 1.0;

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
const resetBtn = document.getElementById('reset-btn');
const sparkBtn = document.getElementById('spark-btn');
const continueBtn = document.getElementById('continue-btn');
const pauseBtn = document.getElementById('pause-btn');
const volumeSlider = document.getElementById('volume-slider');
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

const vnDialogueBox = document.getElementById('vn-dialogue-box');
const vnNameTag = document.getElementById('vn-name-tag');

