import { playAmbientSound } from "./ambient-player.js";

function updatePointsDisplay(points) {
    const marketBalance = document.getElementById("marketBalance");
    const marketPoints = document.getElementById("marketPoints");

    if (marketBalance) marketBalance.textContent = `${points} points`;
    if (marketPoints) marketPoints.textContent = `${points} points`;
}

document.addEventListener("focus-tasks:points-updated", event => {
    updatePointsDisplay(event.detail.points);
});

const topPanelContent = document.getElementById("topPanelContent");
const topPanel = document.getElementById("topPanel");
let marketRequestSequence = 0;


let currentPreview = null;
let currentPreviewButton = null;

function resetPreviewButton() {
    if (currentPreviewButton) {
        currentPreviewButton.textContent = "▷";
    }
    currentPreviewButton = null;
}

function playMusicPreview(url, button) {
    if (!url) return;

    if (currentPreview && currentPreview.src !== url) {
        currentPreview.pause();
        currentPreview.currentTime = 0;
        resetPreviewButton();
        currentPreview = null;
    }

    if (!currentPreview) {
        currentPreview = new Audio(url);
        currentPreview.volume = 0.7;

        currentPreview.addEventListener("ended", () => {
            resetPreviewButton();
            currentPreview = null;
        });
    }

    currentPreviewButton = button;

    currentPreview.play().then(() => {
        button.textContent = "Ⅱ";
    }).catch(error => {
        console.error("Preview playback error:", error);
    });
}

function stopMusicPreview() {
    if (currentPreview) {
        currentPreview.pause();
        currentPreview.currentTime = 0;
        currentPreview = null;
    }

    resetPreviewButton();
}

function resetMusicPreview() {
    if (currentPreview) {
        currentPreview.currentTime = 0;
    }
}


const MUSIC_PRODUCTS = [
    { id: "cat", name: "Cat", description: "Soft purring", icon: "🐈" },
    { id: "rain", name: "Rain", description: "Calm atmosphere", icon: "🌧️" },
    { id: "fire", name: "Fire", description: "Warm and cozy", icon: "🔥" },
    { id: "forest", name: "Forest", description: "Peaceful nature", icon: "🌲" },
    { id: "meditation", name: "Meditation", description: "Relax and breathe", icon: "🧘" },
];

const THEME_PRODUCTS = [
    { id: "woods", name: "Whispering Woods", image: "whispering-woods.png" },
    { id: "neon", name: "Neon Afterglow", image: "neon-afterglow.png" },
    { id: "sakura-coast", name: "Sakura Coast", image: "sakura-coast.png" },
    { id: "burgundy", name: "Burgundy Royale", image: "burgundy-royale.png" },
];

function isCurrentMarketRequest(requestSequence) {
    return requestSequence === marketRequestSequence &&
        !topPanel.hidden &&
        topPanel.dataset.panel === "market";
}



function renderMaterialCards(items) {
    const groups = ["Raw materials", "Construction tools", "Rebuild supplies", "Decorations"];
    const groupIcons = {
        "Raw materials": "🧱",
        "Construction tools": "🛠️",
        "Rebuild supplies": "📦",
    };

    return groups.map(group => {
        const groupItems = items.filter(item => item.group === group);
        if (!groupItems.length) return "";

        return `
            <section class="market-product-section">
                <h3>${group}</h3>
                <div class="market-item-grid">
                    ${groupItems.map(item => `
                        <article class="market-card market-item-card">
                            <div class="market-icon">${item.icon || groupIcons[group]}</div>
                            <div class="market-item-copy">
                                <h3>${item.name}</h3>
                                <strong class="market-price">${item.cost} pts</strong>
                            </div>
                            <small class="market-item-owned-count" data-item-quantity>${item.quantity} owned</small>
                            <button class="market-buy-button"
                                data-buy-market-item="${item.item_id}"
                                data-market-unique="${item.unique ? "true" : "false"}"
                                data-market-owned="${item.unique && item.quantity > 0 ? "true" : "false"}"
                                data-market-unlocked="${item.unlocked !== false ? "true" : "false"}"
                                ${item.unlocked === false || (item.unique && item.quantity > 0) ? "disabled" : ""}>
                                ${item.unlocked === false ? "Unlock after Shelter" : item.unique && item.quantity > 0 ? "Owned ✓" : item.quantity > 0 ? "Buy another" : "Buy"}
                            </button>
                        </article>
                    `).join("")}
                </div>
            </section>
        `;
    }).join("");
}

function renderMarket(catalog) {
    const currentTheme = document.body.dataset.theme || "woods";
    const itemGroups = renderMaterialCards(catalog.items);


    topPanelContent.innerHTML = `
        <div class="market-category-tabs" role="tablist" aria-label="Market categories">
            <button type="button" class="market-category-tab active" role="tab" aria-selected="true" data-market-category="items">Items</button>
            <button type="button" class="market-category-tab" role="tab" aria-selected="false" data-market-category="music">Music</button>
            <button type="button" class="market-category-tab" role="tab" aria-selected="false" data-market-category="themes">Themes</button>
        </div>

        <section class="market-category-panel" role="tabpanel" data-market-panel="items">

            ${itemGroups}
            <p id="marketMessage" class="market-message" aria-live="polite"></p>
        </section>


<section class="market-category-panel" role="tabpanel" data-market-panel="music" hidden>
    <p class="market-category-note">
        Discover music for your focus sessions.
    </p>

    <div id="marketMusicGrid" class="market-grid">
        <p>Loading music...</p>
    </div>

    <p id="marketMusicMessage" class="market-message" aria-live="polite"></p>
</section>


        <section class="market-category-panel" role="tabpanel" data-market-panel="themes" hidden>
            <p class="market-category-note">Your existing themes stay unlocked. Choose one to apply it.</p>
            <div class="theme-grid">
                ${THEME_PRODUCTS.map(theme => `
                    <button type="button" class="theme-card ${currentTheme === theme.id ? "selected" : ""}" data-theme-choice="${theme.id}">
                        <img src="/static/backgrounds/${theme.image}" alt="${theme.name}">
                        <span>${theme.name}</span>
                        <small>${currentTheme === theme.id ? "Currently selected" : "Owned · Select to apply"}</small>
                    </button>
                `).join("")}
            </div>
        </section>
    `;
}


async function loadMarketMusic() {
    const grid = document.getElementById("marketMusicGrid");
    if (!grid) return;

    try {
        const response = await fetch("/api/music");
        if (!response.ok) throw new Error("Music could not be loaded.");

        const tracks = await response.json();
        window.musicTracks = tracks;
        grid.className = "market-item-grid";
        grid.replaceChildren();

        tracks.forEach(track => {
            const card = document.createElement("article");
            card.className = "market-card market-item-card";

            const icon = document.createElement("div");
            icon.className = "market-icon";
            icon.textContent = "♫";

            const copy = document.createElement("div");
            copy.className = "market-item-copy";

            const title = document.createElement("h3");
            title.textContent = track.title;

            const price = document.createElement("strong");
            price.className = "market-price";
            price.textContent = `${track.price} pts`;

            copy.append(title, price);

            const actions = document.createElement("div");
            actions.className = "music-track-actions";

            const play = document.createElement("button");
            play.className = "music-action-button music-play-button";
            play.type = "button";
            play.textContent = "▷";
            play.title = "Play preview";
            play.dataset.musicPlay = track.id;

            const stop = document.createElement("button");
            stop.className = "music-action-button music-stop-button";
            stop.type = "button";
            stop.textContent = "□";
            stop.title = "Stop";
            stop.dataset.musicStop = "true";

            const favorite = document.createElement("button");
            favorite.className = "music-action-button music-favorite-button";
            favorite.type = "button";
            favorite.textContent = "☆";
            favorite.title = "Add to favorites";
            favorite.dataset.musicFavorite = track.id;

            const buy = document.createElement("button");
            buy.className = "music-buy-button";
            buy.type = "button";
            buy.textContent = "Buy";
            buy.dataset.musicBuy = track.id;

            actions.append(play, stop, favorite, buy);
            card.append(icon, copy, actions);
            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Music catalog error:", error);
        grid.textContent = "Music could not be loaded.";
    }
}



function loadMarket() {
    const requestSequence = ++marketRequestSequence;
    topPanelContent.innerHTML = `
        <p class="market-loading">Loading market...</p>
    `;

    fetch("/api/market/catalog")
        .then(response => response.json())
        .then(data => {
            if (!isCurrentMarketRequest(requestSequence)) return;
            if (!data.success) throw new Error("Market could not be loaded.");
            renderMarket(data);
            loadMarketMusic();
        })
        .catch(error => {
            if (!isCurrentMarketRequest(requestSequence)) return;
            topPanelContent.innerHTML = `
                <p class="market-message">${error.message}</p>
            `;
        });
}

document.addEventListener("navigation:panel-open", event => {
    const { panelName } = event.detail;
    const marketBalance = document.getElementById("marketBalance");

    if (marketBalance) marketBalance.hidden = panelName !== "market";

    if (panelName !== "market") {
        marketRequestSequence += 1;
        return;
    }

    fetch("/api/user")
        .then(response => response.json())
        .then(data => updatePointsDisplay(data.points))
        .catch(error => console.error("Points could not load:", error));

    loadMarket();
});

topPanelContent.addEventListener("click", async event => {
        const playButton = event.target.closest("[data-music-play]");




if (playButton && event.currentTarget.contains(playButton)) {
    if (currentPreview && currentPreviewButton === playButton) {
        if (currentPreview.paused) {
            playMusicPreview(currentPreview.src, playButton);
        } else {
            currentPreview.pause();
            playButton.textContent = "▷";
        }
        return;
    }

    const track = window.musicTracks?.find(
        item => item.id === playButton.dataset.musicPlay
    );

    if (track) {
        playMusicPreview(track.preview_url, playButton);
    }
    return;
}

const resetButton = event.target.closest("[data-music-reset]");

if (resetButton && event.currentTarget.contains(resetButton)) {
    resetMusicPreview();
    return;
}


    const categoryButton = event.target.closest("[data-market-category]");
    if (categoryButton && event.currentTarget.contains(categoryButton)) {
        const selectedCategory = categoryButton.dataset.marketCategory;
        topPanelContent.querySelectorAll("[data-market-category]").forEach(button => {
            const selected = button === categoryButton;
            button.classList.toggle("active", selected);
            button.setAttribute("aria-selected", String(selected));
        });
        topPanelContent.querySelectorAll("[data-market-panel]").forEach(panel => {
            panel.hidden = panel.dataset.marketPanel !== selectedCategory;
        });
        return;
    }

    const soundButton = event.target.closest("[data-market-play-sound]");
    if (soundButton && event.currentTarget.contains(soundButton)) {
        await playAmbientSound(soundButton.dataset.marketPlaySound);
        return;
    }

    const itemButton = event.target.closest("[data-buy-market-item]");
    if (itemButton && event.currentTarget.contains(itemButton)) {
        if (itemButton.disabled || itemButton.dataset.purchasePending === "true") return;

        const card = itemButton.closest(".market-card");
        const message = topPanelContent.querySelector("#marketMessage");
        itemButton.dataset.purchasePending = "true";
        itemButton.disabled = true;
        itemButton.textContent = "Processing...";

        try {
            const response = await fetch("/api/market/items/buy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ item_id: itemButton.dataset.buyMarketItem }),
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || "Purchase failed.");
            }

            updatePointsDisplay(result.points);
            const quantity = card.querySelector("[data-item-quantity]");
            if (quantity) quantity.textContent = `${result.quantity} owned`;
            if (message) message.textContent = result.message;
            if (itemButton.dataset.marketUnique === "true") {
                itemButton.dataset.marketOwned = "true";
                itemButton.textContent = "Owned ✓";
            } else {
                itemButton.textContent = "Buy another";
            }
        } catch (error) {
            if (message) message.textContent = error.message;
            itemButton.textContent = "Buy";
        } finally {
            itemButton.disabled = itemButton.dataset.marketOwned === "true" ||
                itemButton.dataset.marketUnlocked === "false";
            delete itemButton.dataset.purchasePending;
        }
        return;
    }

    const buildingButton = event.target.closest("[data-buy-building]");
    if (!buildingButton || !event.currentTarget.contains(buildingButton)) return;
    if (buildingButton.disabled || buildingButton.dataset.purchasePending === "true") return;

    const message = topPanelContent.querySelector("#marketMessage");
    buildingButton.dataset.purchasePending = "true";
    buildingButton.disabled = true;
    buildingButton.textContent = "Processing...";

    try {
        const response = await fetch("/api/building/buy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ building_type: buildingButton.dataset.buyBuilding }),
        });
        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Purchase failed.");
        }

        updatePointsDisplay(result.points);
        if (message) message.textContent = result.message;
        buildingButton.textContent = "Owned ✓";
        setTimeout(() => window.location.reload(), 800);
    } catch (error) {
        if (message) message.textContent = error.message;
        buildingButton.disabled = false;
        buildingButton.textContent = "Buy";
        delete buildingButton.dataset.purchasePending;
    }
});
