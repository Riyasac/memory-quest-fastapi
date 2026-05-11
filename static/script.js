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

function extractErrorMessage(payload, fallback = "Something went wrong") {
    if (!payload) {
        return fallback;
    }

    if (typeof payload === "string") {
        return payload;
    }

    if (typeof payload.detail === "string") {
        return payload.detail;
    }

    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
        const firstError = payload.detail[0];
        if (typeof firstError === "string") {
            return firstError;
        }
        if (firstError && typeof firstError.msg === "string") {
            const location = Array.isArray(firstError.loc)
                ? firstError.loc.filter((part) => part !== "body").pop()
                : null;

            if (!location) {
                return firstError.msg;
            }

            const fieldName = String(location)
                .replace(/_/g, " ")
                .replace(/\b\w/g, (char) => char.toUpperCase());

            const message = firstError.msg.charAt(0).toLowerCase() + firstError.msg.slice(1);
            return `${fieldName} ${message}`;
        }
    }

    return fallback;
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
