// ==========================================
// DIS TRACKING - UNIFIED AUDIO PLAYER
// ==========================================

const soundCards = document.querySelectorAll(".sound-card");

const soundStatus = document.getElementById("soundStatus");
const currentSoundTitle = document.getElementById("currentSoundTitle");
const currentSoundDescription = document.getElementById("currentSoundDescription");
const soundArt = document.querySelector(".sound-art");

const pauseSoundBtn = document.getElementById("pauseSoundBtn");
const stopSoundBtn = document.getElementById("stopSoundBtn");
const soundVolume = document.getElementById("soundVolume");
const volumeValue = document.getElementById("volumeValue");

// ONE shared audio player
const player = new Audio();

const ownedTrackPreloads = new Map();

export function preloadOwnedTrack(url) {
    if (!url) return Promise.resolve(url);

    if (!ownedTrackPreloads.has(url)) {
        const preloadPromise = fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Track preload failed");
                }
                return response.blob();
            })
            .then(blob => URL.createObjectURL(blob))
            .catch(error => {
                console.warn("Track preload failed, using original URL:", error);
                return url;
            });

        ownedTrackPreloads.set(url, preloadPromise);
    }

    return ownedTrackPreloads.get(url);
}

player.volume = Number(soundVolume?.value ?? 0.6);

let currentSoundCard = null;
let currentTrack = null;


// ==========================================
// UI HELPERS
// ==========================================

function updateSoundStatus(message, isPlaying = false) {
    if (!soundStatus) return;

    soundStatus.innerHTML = `
        <span class="status-dot"></span>
        ${message}
    `;

    soundStatus.classList.toggle("is-playing", isPlaying);
}


function updatePlayButton(isPlaying) {
    if (!pauseSoundBtn) return;

    pauseSoundBtn.textContent = isPlaying ? "❚❚" : "▶";

    pauseSoundBtn.setAttribute(
        "aria-label",
        isPlaying ? "Pause sound" : "Resume sound"
    );
}


function clearActiveCards() {
    soundCards.forEach(card => {
        card.classList.remove("active");
    });
}


function updateNowPlaying({
    title,
    description = "",
    icon = "🎧"
}) {
    if (currentSoundTitle) {
        currentSoundTitle.textContent = title;
    }

    if (currentSoundDescription) {
        currentSoundDescription.textContent = description;
    }

    if (soundArt) {
        soundArt.textContent = icon;
    }
}


// ==========================================
// AMBIENT FAVORITES
// ==========================================

const AMBIENT_FAVORITES_KEY = "disTrackingAmbientFavorites";

function getAmbientFavorites() {
    return JSON.parse(
        localStorage.getItem(AMBIENT_FAVORITES_KEY) || "[]"
    );
}

function saveAmbientFavorites(favorites) {
    localStorage.setItem(
        AMBIENT_FAVORITES_KEY,
        JSON.stringify(favorites)
    );
}


function renderAmbientFavorites() {
    const list = document.getElementById("ambientFavoritesList");
    if (!list) return;

    list.replaceChildren();

    const favorites = getAmbientFavorites();

   if (favorites.length === 0) {
    const musicFavorites = document.querySelectorAll(
        "#favoritesList .owned-music-row"
    );

    if (musicFavorites.length === 0) {
        const empty = document.createElement("p");
        empty.className = "music-library-empty";
        empty.textContent = "Your favorite tracks will appear here.";
        list.appendChild(empty);
    }

    return;
}

    favorites.forEach(soundName => {
        const originalCard = Array.from(soundCards).find(
            card => card.dataset.sound === soundName
        );

        if (!originalCard) return;

        const card = originalCard.cloneNode(true);
        const playBtn = card.querySelector(".sound-play-btn");
        const favoriteBtn = card.querySelector(".sound-favorite-btn");

        favoriteBtn.classList.add("active");
        favoriteBtn.textContent = "♥";
        favoriteBtn.setAttribute("aria-pressed", "true");

        playBtn?.addEventListener("click", event => {
            event.stopPropagation();
            playAmbientSound(soundName);
        });

        favoriteBtn?.addEventListener("click", event => {
            event.stopPropagation();

            const updated = getAmbientFavorites().filter(
                item => item !== soundName
            );

            saveAmbientFavorites(updated);
            updateAmbientFavoriteButtons();
            renderAmbientFavorites();
        });

        card.addEventListener("click", () => {
            playAmbientSound(soundName);
        });

        list.appendChild(card);
    });
}


function updateAmbientFavoriteButtons() {
    const favorites = getAmbientFavorites();

    soundCards.forEach(card => {
        const button = card.querySelector(".sound-favorite-btn");
        if (!button) return;

        const isFavorite = favorites.includes(card.dataset.sound);

        button.classList.toggle("active", isFavorite);
        button.textContent = isFavorite ? "♥" : "♡";
        button.setAttribute("aria-pressed", String(isFavorite));
    });
}


// ==========================================
// SHARED PLAY FUNCTION
// ==========================================

export async function playAudioTrack({
    url,
    title,
    artist = "",
    icon = "🎵",
    loop = false,
    type = "music"
}) {
    if (!url) {
        updateSoundStatus("Audio URL not found");
        return false;
    }

    try {
        player.pause();
        player.src = url;
        player.loop = loop;

        currentTrack = {
            title,
            artist,
            type
        };

        currentSoundCard = null;
        clearActiveCards();

        updateNowPlaying({
            title,
            description: artist || (
                type === "ambience" ? "Ambient sound" : "Your music"
            ),
            icon
        });

        await player.play();

        updatePlayButton(true);
        updateSoundStatus("Playing", true);

        return true;

    } catch (error) {
        console.error("Audio playback error:", error);
        updatePlayButton(false);
        updateSoundStatus("Could not play audio");

        return false;
    }
}


// ==========================================
// FREE AMBIENCE SOUNDS
// ==========================================


const AMBIENT_AUDIO_FILES = {
    cat: "Cat.mp3",
    rain: "Rain.mp3",
    fire: "Fire.mp3",
    forest: "Enchanted forest.mp3",
    meditation: "Meditation.mp3"
};

export async function playAmbientSound(soundName) {
    const card = Array.from(soundCards).find(
        item => item.dataset.sound === soundName
    );

    if (!card) {
        console.error("Sound card not found:", soundName);
        return false;
    }

    const fileName = AMBIENT_AUDIO_FILES[soundName];

    if (!fileName) {
        console.error("Ambient audio file not found:", soundName);
        updateSoundStatus("Ambient sound not found");
        return false;
    }

    const audioUrl = `/static/audio/${encodeURIComponent(fileName)}`;

    const icon =
        card.querySelector(".sound-card-icon")?.textContent || "🎧";

    const success = await playAudioTrack({
        url: audioUrl,
        title: card.dataset.title || soundName,
        artist: card.dataset.description || "",
        icon,
        loop: true,
        type: "ambience"
    });

    if (success) {
        card.classList.add("active");
    }

    return success;
}


export async function playOwnedTrack(track) {
    if (!track || !track.audio_url) {
        updateSoundStatus("Track is unavailable");
        return false;
    }

    // Update selected track immediately
    currentTrack = {
        title: track.title,
        artist: track.artist || "",
        type: "music"
    };

    currentSoundCard = null;
    clearActiveCards();

    updateNowPlaying({
        title: track.title,
        description: track.artist || "Your music",
        icon: "🎵"
    });

    updateSoundStatus("Loading...");

    const playbackUrl = await preloadOwnedTrack(track.audio_url);

    return playAudioTrack({
        url: playbackUrl,
        title: track.title,
        artist: track.artist || "",
        icon: "🎵",
        loop: true,
        type: "music"
    });
}
// ==========================================
// PAUSE / RESUME
// ==========================================

pauseSoundBtn?.addEventListener("click", async () => {
    if (!player.src) {
        updateSoundStatus("Choose a sound first");
        return;
    }

    if (player.paused) {
        try {
            await player.play();
            updatePlayButton(true);
            updateSoundStatus("Playing", true);

        } catch (error) {
            console.error(error);
            updateSoundStatus("Could not resume audio");
        }

    } else {
        player.pause();
        updatePlayButton(false);
        updateSoundStatus("Paused");
    }
});


// ==========================================
// STOP
// ==========================================

stopSoundBtn?.addEventListener("click", () => {
    player.pause();
    player.currentTime = 0;
    player.removeAttribute("src");
    player.load();

    currentTrack = null;
    currentSoundCard = null;

    clearActiveCards();

    updatePlayButton(false);
    updateSoundStatus("Choose a sound");

    updateNowPlaying({
        title: "No sound selected",
        description: "Choose your ambience or music",
        icon: "🎧"
    });
});


// ==========================================
// AMBIENCE CARD EVENTS
// ==========================================

soundCards.forEach(card => {
    card.addEventListener("click", () => {
        playAmbientSound(card.dataset.sound);
    });

    const favoriteBtn = card.querySelector(".sound-favorite-btn");

    favoriteBtn?.addEventListener("click", event => {
    event.stopPropagation();

    const soundName = card.dataset.sound;
    const favorites = getAmbientFavorites();

    const updated = favorites.includes(soundName)
        ? favorites.filter(item => item !== soundName)
        : [...favorites, soundName];

    saveAmbientFavorites(updated);
    updateAmbientFavoriteButtons();
    renderAmbientFavorites();
});
});


// ==========================================
// VOLUME
// ==========================================

soundVolume?.addEventListener("input", () => {
    const volume = Number(soundVolume.value);

    player.volume = volume;

    if (volumeValue) {
        volumeValue.textContent = `${Math.round(volume * 100)}%`;
    }
});


// ==========================================
// PLAYER EVENTS
// ==========================================

player.addEventListener("ended", () => {
    if (currentTrack?.type === "music") {
        updatePlayButton(false);
        updateSoundStatus("Finished");
    }
});

player.addEventListener("error", () => {
    updatePlayButton(false);
    updateSoundStatus("Audio playback error");
});

updateAmbientFavoriteButtons();
renderAmbientFavorites();