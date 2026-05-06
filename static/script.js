const MAX_LEVEL = 100;
let board = [];
let revealed = [];
let matched = [];
let moves = 0;
let currentGameId = null;
let currentLevel = 1;
let playerName = "";
let infoTimer = null;

function getAuthHeaders(extraHeaders = {}) {
    const token = sessionStorage.getItem("token");
    return {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...extraHeaders,
    };
}

async function apiFetch(url, options = {}) {
    const headers = getAuthHeaders(options.headers || {});
    return fetch(url, { ...options, headers });
}

async function init() {
    if (!sessionStorage.getItem("token")) {
        window.location.href = "/login";
        return;
    }

    playerName = sessionStorage.getItem("playerName");
    if (!playerName) {
        window.location.href = "/login";
        return;
    }

    window.headers = getAuthHeaders();
}

function logOut() {
    if (typeof window.pauseGameTimer === "function") {
        window.pauseGameTimer();
    }
    sessionStorage.clear();
    window.location.href = "/login";
}

function goToLevels() {
    if (typeof window.pauseGameTimer === "function") {
        window.pauseGameTimer();
    }
    window.location.href = "/game/levels";
}

function goToProfile() {
    if (typeof window.pauseGameTimer === "function") {
        window.pauseGameTimer();
    }
    window.location.href = "/game/profile";
}

function goToAbout() {
    if (typeof window.pauseGameTimer === "function") {
        window.pauseGameTimer();
    }
    window.location.href = "/game/about";
}

function gotToLeaderboard() {
    window.location.href = "/game/ranks";
}
