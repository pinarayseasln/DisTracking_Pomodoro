import { apiPost } from "./api.js";

    const timerDisplay = document.getElementById("timer");
    const startBtn = document.getElementById("startBtn");
    const resetBtn = document.getElementById("resetBtn");
    const modeButtons = document.querySelectorAll("[data-mode]");
    const focusMinutesInput = document.getElementById("focusMinutes");
    const completionSoundInput = document.getElementById("completionSound");
    const timerNotice = document.getElementById("timerNotice");


    let savedFocusMinutes = Number(localStorage.getItem("focusMinutes"));
    if (!Number.isInteger(savedFocusMinutes) || savedFocusMinutes < 1 || savedFocusMinutes > 180) {
        savedFocusMinutes = 25;
    }
    focusMinutesInput.value = savedFocusMinutes;
    completionSoundInput.checked = localStorage.getItem("completionSound") === "true";

    const durations = {
        focus: savedFocusMinutes * 60,
        short: 5 * 60,
        long: 15 * 60
    };

    let currentMode = "focus";
    let remainingSeconds = durations[currentMode];
    let totalSeconds = remainingSeconds;
    let interval = null;
    let timerSession = null;
    let sessionAnchorMs = null;
    let lastHeartbeatMs = 0;
    let completionPending = false;

    function updateDisplay() {
        const minutes = Math.floor(remainingSeconds / 60);

        const seconds = remainingSeconds % 60;


        timerDisplay.textContent =
            String(minutes).padStart(2, "0") + ":" +
            String(seconds).padStart(2, "0");
            const percent = (remainingSeconds / totalSeconds) * 100;
document.querySelector('.timer').style.setProperty('--progress', percent);
    }

    function stopTimer() {
        clearInterval(interval);
        interval = null;
        startBtn.textContent = "Start";
    }

    function applySession(session) {
        timerSession = session;
        if (!session) return;
        currentMode = session.mode;
        modeButtons.forEach(button => button.classList.toggle("selected", button.dataset.mode === currentMode));
        totalSeconds = session.duration_seconds;
        if (currentMode === "focus") {
            focusMinutesInput.value = session.duration_seconds / 60;
            durations.focus = session.duration_seconds;
        }
        remainingSeconds = session.remaining_seconds;
        sessionAnchorMs = session.status === "running" ? Date.now() : null;
        lastHeartbeatMs = Date.now();
        startBtn.textContent = session.status === "running" ? "Pause" : "Resume";
        const questPanel = document.getElementById("topPanelContent");
        if (session.quest_id === null) {
            delete questPanel.dataset.activeQuestId;
        } else {
            questPanel.dataset.activeQuestId = String(session.quest_id);
        }
        document.dispatchEvent(new CustomEvent("pomodoro:quest-session-state", {
            detail: { questId: session.quest_id }
        }));
        updateDisplay();
    }

    function timerTick() {
        if (!timerSession || timerSession.status !== "running") return;
        const elapsedSinceCheckpoint = Math.floor((Date.now() - sessionAnchorMs) / 1000);
        remainingSeconds = Math.max(0, timerSession.remaining_seconds - elapsedSinceCheckpoint);
        updateDisplay();

        if (Date.now() - lastHeartbeatMs >= 5000) {
            lastHeartbeatMs = Date.now();
            const heartbeatSessionId = timerSession.id;
            apiPost("/api/pomodoro/heartbeat", { session_id: timerSession.id })
                .then(data => {
                    if (!completionPending && timerSession && timerSession.id === heartbeatSessionId) {
                        applySession(data.session);
                    }
                })
                .catch(error => {
                    if (!completionPending && timerSession && timerSession.id === heartbeatSessionId && error.data && error.data.session) {
                        applySession(error.data.session);
                    }
                    else console.error("Timer heartbeat failed:", error);
                });
        }

        if (remainingSeconds <= 0 && !completionPending) finishSession();
    }

    function startTicker() {
        clearInterval(interval);
        interval = setInterval(timerTick, 250);
        startBtn.textContent = "Pause";
    }

    async function finishSession() {
        if (!timerSession || completionPending) return;
        completionPending = true;
        stopTimer();
        try {
            const completedSession = timerSession;
            const data = await apiPost("/api/pomodoro/complete", { session_id: completedSession.id });
            timerSession = null;
            sessionAnchorMs = null;
            timerNotice.hidden = true;
            playCompletionSound();

            if (completedSession.mode === "focus") {
                document.dispatchEvent(new CustomEvent("focus-tasks:points-updated", { detail: { points: data.points } }));
                document.dispatchEvent(new CustomEvent("pomodoro:completion-modal-open", {
                    detail: {
                        pointsEarned: data.earned_points,
                        totalPoints: data.points
                    }
                }));
                if (completedSession.quest_id !== null) {
                    const questUpdate = new CustomEvent("pomodoro:quest-session-completed", {
                        detail: { questId: completedSession.quest_id, completion: null }
                    });
                    document.dispatchEvent(questUpdate);
                    await questUpdate.detail.completion;
                }
            } else {
                alert("Break is over. Ready to focus again?");
            }
            remainingSeconds = durations[currentMode];
            totalSeconds = remainingSeconds;
            updateDisplay();
        } catch (error) {
            if (error.data && error.data.session) {
                applySession(error.data.session);
                if (error.data.session.status === "running") startTicker();
            } else {
                showCompletionNotice(error.message);
            }
        } finally {
            completionPending = false;
        }
    }

    async function resetTimer() {
        stopTimer();
        if (timerSession) {
            try {
                await apiPost("/api/pomodoro/reset", { session_id: timerSession.id });
            } catch (error) {
                console.error("Timer session could not be cancelled:", error);
            }
        }
        timerSession = null;
        sessionAnchorMs = null;
        timerNotice.hidden = true;
        remainingSeconds = durations[currentMode];
        totalSeconds = remainingSeconds;
        updateDisplay();
        document.querySelector('.timer').style.setProperty('--progress', 100);
    }

    focusMinutesInput.addEventListener("change", () => {
        const minutes = Math.max(1, Math.min(180, Math.round(Number(focusMinutesInput.value) || 25)));
        focusMinutesInput.value = minutes;
        durations.focus = minutes * 60;
        localStorage.setItem("focusMinutes", String(minutes));
        if (currentMode === "focus") resetTimer();
    });

    completionSoundInput.addEventListener("change", () => {
        localStorage.setItem("completionSound", String(completionSoundInput.checked));
        if (completionSoundInput.checked) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioContext = audioContext || new AudioContextClass();
                if (audioContext.state === "suspended") audioContext.resume().catch(() => {});
            }
        }
    });

    let audioContext = null;

    function showCompletionNotice(message) {
        timerNotice.textContent = message;
        timerNotice.hidden = false;
    }



    function playCompletionSound() {
        if (!completionSoundInput.checked) return;
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) return;
        audioContext = audioContext || new AudioContextClass();
        const playChime = () => {
            [660, 880].forEach((frequency, index) => {
                const startAt = audioContext.currentTime + index * 0.25;
                const oscillator = audioContext.createOscillator();
                const volume = audioContext.createGain();
                oscillator.type = "sine";
                oscillator.frequency.value = frequency;
                volume.gain.setValueAtTime(0.0001, startAt);
                volume.gain.exponentialRampToValueAtTime(0.06, startAt + 0.03);
                volume.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.22);
                oscillator.connect(volume);
                volume.connect(audioContext.destination);
                oscillator.start(startAt);
                oscillator.stop(startAt + 0.23);
            });
        };
        if (audioContext.state === "running") playChime();
        else audioContext.resume().then(playChime).catch(() => {});
    }
    async function startTimer() {
        if (timerSession && timerSession.status === "running") {
            stopTimer();
            try {
                applySession((await apiPost("/api/pomodoro/pause", { session_id: timerSession.id })).session);
            } catch (error) {
                showCompletionNotice(error.message);
            }
            return;
        }
        if (completionSoundInput.checked && audioContext && audioContext.state === "suspended") {
            audioContext.resume().catch(() => {});
        }
        try {
            if (timerSession && timerSession.status === "paused") {
                applySession((await apiPost("/api/pomodoro/resume", { session_id: timerSession.id })).session);
            } else {
                const data = await apiPost("/api/pomodoro/start", {
                    mode: currentMode,
                    duration_seconds: durations[currentMode],
                    quest_id: currentMode === "focus"
                        ? (document.getElementById("topPanelContent").dataset.activeQuestId || null)
                        : null
                });
                applySession(data.session);
            }
            timerNotice.hidden = true;
            startTicker();
        } catch (error) {
            if (error.data && error.data.session) applySession(error.data.session);
            showCompletionNotice(error.message);
        }
    }

    modeButtons.forEach(button => {
        button.addEventListener("click", async () => {
            await resetTimer();
            currentMode = button.dataset.mode;

            modeButtons.forEach(item => {
                item.classList.remove("selected");
            });

            button.classList.add("selected");
            remainingSeconds = durations[currentMode];
            totalSeconds = remainingSeconds;
            updateDisplay();
        });
    });

    startBtn.addEventListener("click", startTimer);
    resetBtn.addEventListener("click", resetTimer);

    fetch("/api/pomodoro/session")
        .then(response => response.json())
        .then(data => {
            if (data.session) {
                applySession(data.session);
                if (data.session.status === "running") startTicker();
            }
        })
        .catch(error => console.error("Could not restore timer session:", error));

    window.addEventListener("pagehide", () => {
        if (!timerSession || timerSession.status !== "running") return;
        const body = new Blob(
            [JSON.stringify({ session_id: timerSession.id })],
            { type: "application/json" }
        );
        navigator.sendBeacon("/api/pomodoro/pause", body);
    });

    updateDisplay();
