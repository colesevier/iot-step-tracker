// --- Parameters ---
const SAMPLE_INTERVAL_MS = 40;      // ~25 Hz
const SEND_INTERVAL_MS = 5000;      // send to server every 5s
const ALERT_INTERVAL_MS = 5000;     // poll alerts every 5s

const WINDOW_SIZE = 20;
const THRESHOLD = 0.8;
const MIN_STEP_INTERVAL_MS = 300;

// Simple estimates
const STEP_LENGTH_M = 0.78;         // avg step length
const CALORIES_PER_STEP = 0.04;     // extremely rough estimate

// --- State ---
let magnitudes = [];
let lastSampleTime = 0;
let lastStepTime = 0;

let totalSteps = 0;
let unsentSteps = 0;

let sampling = false;
let sendTimer = null;
let alertTimer = null;
let sessionStartTime = null;
let sessionTimer = null;

// --- UI elements ---
const statusEl = document.getElementById("status");
const totalStepsEl = document.getElementById("totalSteps");
const unsentStepsEl = document.getElementById("unsentSteps");
const lastAlertEl = document.getElementById("lastAlert");
const deviceIdInput = document.getElementById("deviceId");

const sessionTimeEl = document.getElementById("sessionTime");
const distanceKmEl = document.getElementById("distanceKm");
const caloriesEl = document.getElementById("calories");

const permBtn = document.getElementById("permBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const resetBtn = document.getElementById("resetBtn");

function updateNumbers() {
  totalStepsEl.textContent = String(totalSteps);
  unsentStepsEl.textContent = String(unsentSteps);

  const distanceMeters = totalSteps * STEP_LENGTH_M;
  const distanceKm = distanceMeters / 1000.0;
  distanceKmEl.textContent = distanceKm.toFixed(2);

  const calories = totalSteps * CALORIES_PER_STEP;
  caloriesEl.textContent = Math.round(calories);
}

function updateSessionTime() {
  if (!sessionStartTime) {
    sessionTimeEl.textContent = "00:00";
    return;
  }
  const now = new Date();
  const diffSec = Math.floor((now - sessionStartTime) / 1000);
  const minutes = String(Math.floor(diffSec / 60)).padStart(2, "0");
  const seconds = String(diffSec % 60).padStart(2, "0");
  sessionTimeEl.textContent = `${minutes}:${seconds}`;
}

function handleMotion(event) {
  if (!sampling) return;

  const now = performance.now();
  if (now - lastSampleTime < SAMPLE_INTERVAL_MS) return;
  lastSampleTime = now;

  const acc = event.accelerationIncludingGravity || event.acceleration;
  if (!acc) return;

  const ax = acc.x || 0;
  const ay = acc.y || 0;
  const az = acc.z || 0;

  const mag = Math.sqrt(ax * ax + ay * ay + az * az);
  magnitudes.push(mag);
  if (magnitudes.length > WINDOW_SIZE) magnitudes.shift();
  if (magnitudes.length < WINDOW_SIZE) return;

  const avg = magnitudes.reduce((a, b) => a + b, 0) / magnitudes.length;
  const filtered = mag - avg;

  if (filtered > THRESHOLD && (now - lastStepTime) >= MIN_STEP_INTERVAL_MS) {
    lastStepTime = now;
    totalSteps += 1;
    unsentSteps += 1;
    updateNumbers();
  }
}

async function sendStepsToServer() {
  const deviceId = deviceIdInput.value.trim() || "iphone_browser_1";
  const stepsToSend = unsentSteps;
  if (stepsToSend <= 0) return;

  const payload = {
    device_id: deviceId,
    steps: stepsToSend,
    timestamp: new Date().toISOString(),
  };

  try {
    const res = await fetch("/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      console.error("sendSteps error HTTP", res.status);
      statusEl.textContent = `Send error: HTTP ${res.status}`;
      return;
    }
    console.log("Sent steps:", stepsToSend);
    unsentSteps = 0;
    updateNumbers();
  } catch (err) {
    console.error("sendSteps error", err);
    statusEl.textContent = `Send error: ${err}`;
  }
}

async function checkAlertFromServer() {
  const deviceId = deviceIdInput.value.trim() || "iphone_browser_1";

  try {
    const res = await fetch(`/alert/${encodeURIComponent(deviceId)}`);
    if (!res.ok) {
      console.error("alert error HTTP", res.status);
      return;
    }
    const data = await res.json();
    if (data.alert) {
      console.log("ALERT:", data.alert);
      lastAlertEl.textContent = data.alert;
      if (navigator.vibrate) navigator.vibrate(200);
    }
  } catch (err) {
    console.error("alert error", err);
  }
}

async function resetSessionOnServer() {
  const deviceId = deviceIdInput.value.trim() || "iphone_browser_1";
  try {
    const res = await fetch(`/user/${encodeURIComponent(deviceId)}/reset`, {
      method: "POST",
    });
    if (!res.ok) {
      console.error("reset error HTTP", res.status);
      statusEl.textContent = `Reset error: HTTP ${res.status}`;
    }
  } catch (err) {
    console.error("reset error", err);
    statusEl.textContent = `Reset error: ${err}`;
  }
}

async function requestMotionPermission() {
  try {
    if (
      typeof DeviceMotionEvent !== "undefined" &&
      typeof DeviceMotionEvent.requestPermission === "function"
    ) {
      const response = await DeviceMotionEvent.requestPermission();
      if (response === "granted") {
        statusEl.textContent = "Motion permission granted. Tap Start.";
        permBtn.disabled = true;
        startBtn.disabled = false;
        window.addEventListener("devicemotion", handleMotion);
      } else {
        statusEl.textContent = "Motion permission denied.";
      }
    } else {
      statusEl.textContent = "Motion events enabled. Tap Start.";
      permBtn.disabled = true;
      startBtn.disabled = false;
      window.addEventListener("devicemotion", handleMotion);
    }
  } catch (err) {
    console.error("Permission error", err);
    statusEl.textContent = `Permission error: ${err}`;
  }
}

function startSampling() {
  if (sampling) return;
  sampling = true;
  statusEl.textContent = "Sampling accelerometer…";
  startBtn.disabled = true;
  stopBtn.disabled = false;
  resetBtn.disabled = false;

  totalSteps = 0;
  unsentSteps = 0;
  magnitudes = [];
  updateNumbers();

  sessionStartTime = new Date();
  updateSessionTime();
  if (sessionTimer) clearInterval(sessionTimer);
  sessionTimer = setInterval(updateSessionTime, 1000);

  sendTimer = setInterval(sendStepsToServer, SEND_INTERVAL_MS);
  alertTimer = setInterval(checkAlertFromServer, ALERT_INTERVAL_MS);
}

function stopSampling() {
  if (!sampling) return;
  sampling = false;
  statusEl.textContent = "Stopped.";
  startBtn.disabled = false;
  stopBtn.disabled = true;

  if (sendTimer) clearInterval(sendTimer);
  if (alertTimer) clearInterval(alertTimer);
  if (sessionTimer) clearInterval(sessionTimer);
  sendTimer = null;
  alertTimer = null;
  sessionTimer = null;
}

async function resetSession() {
  // stop but keep permission
  stopSampling();

  totalSteps = 0;
  unsentSteps = 0;
  magnitudes = [];
  lastAlertEl.textContent = "–";
  sessionStartTime = null;
  updateNumbers();
  updateSessionTime();

  await resetSessionOnServer();
  statusEl.textContent = "Session reset.";
}

permBtn.addEventListener("click", requestMotionPermission);
startBtn.addEventListener("click", startSampling);
stopBtn.addEventListener("click", stopSampling);
resetBtn.addEventListener("click", resetSession);