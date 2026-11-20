// ===== Ambient Sound Player =====

const soundCards = document.querySelectorAll(".sound-card");
const soundStatus = document.getElementById("soundStatus");
const currentSoundTitle = document.getElementById("currentSoundTitle");
const currentSoundDescription = document.getElementById("currentSoundDescription");
const soundArt = document.querySelector(".sound-art");

const pauseSoundBtn = document.getElementById("pauseSoundBtn");
const stopSoundBtn = document.getElementById("stopSoundBtn");
const soundVolume = document.getElementById("soundVolume");
const volumeValue = document.getElementById("volumeValue");

let currentSound = null;
let currentSoundCard = null;

const audioElements = document.querySelectorAll(
    ".ambient-panel audio, audio[id$='Audio']"
);

// Set the starting volume
audioElements.forEach(audio => {
    audio.volume = Number(soundVolume.value);
});

function updateSoundStatus(message, isPlaying = false) {
    soundStatus.innerHTML = `
        <span class="status-dot"></span>
        ${message}
    `;

    soundStatus.classList.toggle("is-playing", isPlaying);
}

function pauseAllSounds() {
    audioElements.forEach(audio => audio.pause());
}

function clearActiveCards() {
    soundCards.forEach(card => card.classList.remove("active"));
}

async function selectSound(card) {
        const soundName = card.dataset.sound;
        const audio = document.getElementById(`${soundName}Audio`);

        if (!audio) {
            console.error(`Audio file not found: ${soundName}`);
            updateSoundStatus("Sound file not found");
            return;
        }

        // Stop the previous sound before playing another one
        pauseAllSounds();

        if (currentSound && currentSound !== audio) {
            currentSound.currentTime = 0;
        }

        currentSound = audio;
        currentSoundCard = card;

        currentSoundTitle.textContent = card.dataset.title;
        currentSoundDescription.textContent = card.dataset.description;
        soundArt.textContent = card.querySelector(".sound-card-icon").textContent;

        clearActiveCards();
        card.classList.add("active");

        try {
            await currentSound.play();

            pauseSoundBtn.textContent = "❚❚";
            pauseSoundBtn.setAttribute("aria-label", "Pause sound");

            updateSoundStatus("Playing", true);
        } catch (error) {
            console.error(error);
            updateSoundStatus("Could not play sound");
        }
}

soundCards.forEach(card => {
    card.addEventListener("click", () => selectSound(card));
});

export async function playAmbientSound(soundName) {
    const card = Array.from(soundCards).find(item => item.dataset.sound === soundName);
    if (!card) return false;
    await selectSound(card);
    return true;
}



// Pause / Resume
pauseSoundBtn.addEventListener("click", async () => {
    if (!currentSound) {
        updateSoundStatus("Choose a sound first");
        return;
    }

    if (currentSound.paused) {
        try {
            await currentSound.play();
            pauseSoundBtn.textContent = "❚❚";
            pauseSoundBtn.setAttribute("aria-label", "Pause sound");
            updateSoundStatus("Playing", true);
        } catch (error) {
            console.error(error);
            updateSoundStatus("Could not resume sound");
        }
    } else {
        currentSound.pause();
        pauseSoundBtn.textContent = "▶";
        pauseSoundBtn.setAttribute("aria-label", "Resume sound");
        updateSoundStatus("Paused");
    }
});



// Stop all sounds and reset
stopSoundBtn.addEventListener("click", () => {
    // Stop every audio file, not just the selected one
    audioElements.forEach(audio => {
        audio.pause();
        audio.currentTime = 0;
    });

    currentSound = null;
    currentSoundCard = null;

    pauseSoundBtn.textContent = "▶";
    pauseSoundBtn.setAttribute("aria-label", "Play sound");

    clearActiveCards();
    updateSoundStatus("Choose a sound");

    currentSoundTitle.textContent = "No sound selected";
    currentSoundDescription.textContent = "Choose your ambience";
    soundArt.textContent = "🎧";
});


// Volume slider
soundVolume.addEventListener("input", () => {
    const volume = Number(soundVolume.value);

    audioElements.forEach(audio => {
        audio.volume = volume;
    });

    volumeValue.textContent = `${Math.round(volume * 100)}%`;
});
