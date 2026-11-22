import {
    playAmbientSound,
    playOwnedTrack,
    preloadOwnedTrack
} from "./ambient-player.js";

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
let favoriteTrackIds = new Set();
let currentPreviewButton = null;

function preloadOwnedTrackOnHover(button) {
    const url = button.dataset.audioUrl;

    if (url) {
        preloadOwnedTrack(url);
    }
}

document.addEventListener("pointerover", event => {
    const button = event.target.closest("[data-play-owned-track]");

    if (button) {
        preloadOwnedTrackOnHover(button);
    }
});

document.addEventListener("focusin", event => {
    const button = event.target.closest("[data-play-owned-track]");

    if (button) {
        preloadOwnedTrackOnHover(button);
    }
});

document.addEventListener("pointerover", event => {
    const button = event.target.closest("[data-play-owned-track]");

    if (button) {
        preloadOwnedTrack(button);
    }
});

document.addEventListener("focusin", event => {
    const button = event.target.closest("[data-play-owned-track]");

    if (button) {
        preloadOwnedTrack(button);
    }
});

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
            <button type="button" class="market-category-tab" role="tab" aria-selected="false" data-market-category="wishlist">Wishlist </button>
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
        <section class="market-category-panel" role="tabpanel" data-market-panel="wishlist" hidden>
    <p class="market-category-note"><b>
        Your saved music and themes will appear here.</b>
    </p>

    <div id="marketWishlistGrid" class="market-item-grid">
        <p>Loading wishlist...</p>
    </div>
</section>


    `;
}



let marketPreviewAudio = null;
let marketPreviewTimeout = null;

function stopMarketPreview() {
    if (marketPreviewTimeout) {
        clearTimeout(marketPreviewTimeout);
        marketPreviewTimeout = null;
    }

    if (marketPreviewAudio) {
        marketPreviewAudio.pause();
        marketPreviewAudio.currentTime = 0;
        marketPreviewAudio = null;
    }
}

async function loadOwnedMusic() {
    const list = document.getElementById("ownedMusicList");
    if (!list) return;

    try {
        const [libraryResponse, favoritesResponse] = await Promise.all([
            fetch("/api/music/library"),
            fetch("/api/music/favorites")
        ]);

        if (!libraryResponse.ok || !favoritesResponse.ok) {
            throw new Error("Library could not be loaded.");
        }

        const libraryData = await libraryResponse.json();
        const favoritesData = await favoritesResponse.json();

        const tracks = Array.isArray(libraryData)
            ? libraryData
            : (libraryData.tracks || []);

        const favorites = new Set(favoritesData.favorites || []);

        list.replaceChildren();

        if (!tracks.length) {
    list.replaceChildren();
    renderFavorites([]);
    return;
}

        tracks.forEach(track => {
            const row = document.createElement("div");
            row.className = "owned-music-row";

            const info = document.createElement("div");
            info.className = "owned-music-info";

            const title = document.createElement("strong");
            title.textContent = track.title;

            const artist = document.createElement("small");
            artist.textContent = track.artist || "Unknown artist";

            info.append(title, artist);

            const actions = document.createElement("div");
            actions.className = "owned-music-actions";

            const playButton = document.createElement("button");
            playButton.type = "button";
            playButton.textContent = "▶";

            playButton.dataset.playOwnedTrack = track.id;
            playButton.dataset.audioUrl = track.audio_url || "";
            playButton.dataset.trackTitle = track.title || "";
            playButton.dataset.trackArtist = track.artist || "";


            const favoriteButton = document.createElement("button");
            favoriteButton.type = "button";
            favoriteButton.textContent = favorites.has(track.id) ? "♥" : "  ♡";
            favoriteButton.className = "music-favorite-button";
            favoriteButton.dataset.toggleFavorite = track.id;
            favoriteButton.dataset.favorite = String(favorites.has(track.id));

            actions.append(playButton, favoriteButton);
            row.append(info, actions);
            list.appendChild(row);
        });

        renderFavorites(tracks.filter(track => favorites.has(track.id)));

    } catch (error) {
        console.error("Owned music error:", error);
        list.textContent = "Your music library could not be loaded.";
    }
}

function renderFavorites(tracks) {
   const list = document.getElementById("favoriteTracksList");
    if (!list) return;

    list.replaceChildren();

    if (!tracks.length) {
        const empty = document.createElement("p");
        empty.className = "music-library-empty";
        empty.textContent = "Your favorite tracks will appear here.";
        list.appendChild(empty);
        return;
    }

    tracks.forEach(track => {
        const row = document.createElement("div");
        row.className = "owned-music-row";

        const info = document.createElement("div");
        info.className = "owned-music-info";

        const title = document.createElement("strong");
        title.textContent = track.title;

        const artist = document.createElement("small");
        artist.textContent = track.artist || "Unknown artist";

        info.append(title, artist);

        const actions = document.createElement("div");
        actions.className = "owned-music-actions";

        const playButton = document.createElement("button");
        playButton.type = "button";
        playButton.className = "sound-play-btn";
        playButton.textContent = "▶";

        playButton.dataset.playOwnedTrack = track.id;
        playButton.dataset.audioUrl = track.audio_url || "";
        playButton.dataset.trackTitle = track.title || "";
        playButton.dataset.trackArtist = track.artist || "";

        const favoriteButton = document.createElement("button");
        favoriteButton.type = "button";
        favoriteButton.textContent = "♥";
        favoriteButton.className = "music-favorite-button";
        favoriteButton.dataset.toggleFavorite = track.id;
        favoriteButton.dataset.favorite = "true";

        actions.append(playButton, favoriteButton);
        row.append(info, actions);
        list.appendChild(row);
    });
}

function updateFavoriteTracksUI(button, isFavorite) {
    const list = document.getElementById("favoriteTracksList");
    if (!list) return;

    const trackId = button.dataset.toggleFavorite;

    // Aynı parçanın bütün kalp butonlarını güncelle
    document.querySelectorAll("[data-toggle-favorite]").forEach(item => {
        if (item.dataset.toggleFavorite === trackId) {
            item.dataset.favorite = String(isFavorite);
            item.textContent = isFavorite ? " ♥" : " ♡";
        }
    });

    const existingButton = Array.from(
        list.querySelectorAll("[data-toggle-favorite]")
    ).find(item => item.dataset.toggleFavorite === trackId);

    if (isFavorite) {
        if (!existingButton) {
            const sourceRow = button.closest(".owned-music-row");

            if (sourceRow && !list.contains(sourceRow)) {
                const newRow = sourceRow.cloneNode(true);

                const newButton = newRow.querySelector("[data-toggle-favorite]");
                newButton.dataset.favorite = "true";
                newButton.textContent = " ♥";

                list.querySelector(".music-library-empty")?.remove();
                list.appendChild(newRow);
            }
        }
    } else if (existingButton) {
        existingButton.closest(".owned-music-row")?.remove();
    }

    const hasFavorites = list.querySelector("[data-toggle-favorite]");

    if (!hasFavorites && !list.querySelector(".music-library-empty")) {
        const empty = document.createElement("p");
        empty.className = "music-library-empty";
        empty.textContent = "Your favorite tracks will appear here.";
        list.appendChild(empty);
    }
}

async function loadMarketMusic() {
    const grid = document.getElementById("marketMusicGrid");
    if (!grid) return;

    try {
        const [musicResponse, wishlistResponse, libraryResponse] = await Promise.all([
            fetch("/api/music"),
            fetch("/api/music/wishlist"),
            fetch("/api/music/library")
        ]);

        if (!musicResponse.ok) throw new Error("Music could not be loaded.");

        const tracks = await musicResponse.json();

        const wishlistData = wishlistResponse.ok
            ? await wishlistResponse.json()
            : { wishlist: [] };

        const libraryData = libraryResponse.ok
            ? await libraryResponse.json()
            : [];

        const wishlist = new Set(wishlistData.wishlist || []);
        const ownedTracks = Array.isArray(libraryData)
            ? libraryData
            : (libraryData.tracks || []);
        const owned = new Set(ownedTracks.map(track => track.id));

        grid.className = "market-item-grid";
        grid.replaceChildren();

        if (!tracks.length) {
            grid.textContent = "No music available yet.";
            return;
        }

        tracks.forEach(track => {
            const card = document.createElement("article");
            card.className = "market-card market-item-card";

            const icon = document.createElement("div");
            icon.className = "market-icon";
            icon.textContent = "🎵";

            const copy = document.createElement("div");
            copy.className = "market-item-copy";

            const title = document.createElement("h3");
            title.textContent = track.title;

            const artist = document.createElement("small");
            artist.textContent = track.artist || "Unknown artist";

            const price = document.createElement("strong");
            price.className = "market-price";
            price.textContent = `${track.price} pts`;

            copy.append(title, artist, price);
            card.append(icon, copy);

            const actions = document.createElement("div");
            actions.className = "market-music-actions";

            if (track.preview_url) {
                const previewButton = document.createElement("button");
                previewButton.type = "button";
                previewButton.textContent = "▶ Preview";
                previewButton.dataset.previewTrack = track.id;
                previewButton.dataset.previewUrl = track.preview_url;
                actions.appendChild(previewButton);
            }

            const wishlistButton = document.createElement("button");
            wishlistButton.type = "button";
            wishlistButton.textContent = wishlist.has(track.id)
                ? "★ Wishlisted"
                : "☆  Wishlist";
            wishlistButton.dataset.toggleWishlist = track.id;
            wishlistButton.dataset.wishlisted = String(wishlist.has(track.id));
            actions.appendChild(wishlistButton);

            const buyButton = document.createElement("button");
            buyButton.type = "button";
            buyButton.className = "market-buy-button";
            buyButton.dataset.buyMusic = track.id;
            buyButton.textContent = owned.has(track.id) ? "Owned ✓" : "Buy";
            buyButton.disabled = owned.has(track.id);
            actions.appendChild(buyButton);

            card.appendChild(actions);
            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Music catalog error:", error);
        grid.textContent = "Music could not be loaded.";
    }
}


async function loadMarketWishlist() {
    const grid = document.getElementById("marketWishlistGrid");
    if (!grid) return;

    try {
        const [wishlistResponse, musicResponse] = await Promise.all([
            fetch("/api/music/wishlist"),
            fetch("/api/music")
        ]);

        if (!wishlistResponse.ok || !musicResponse.ok) {
            throw new Error("Wishlist could not be loaded.");
        }

        const wishlistData = await wishlistResponse.json();
        const tracks = await musicResponse.json();

        const wishlist = new Set(wishlistData.wishlist || []);
        const savedTracks = tracks.filter(track => wishlist.has(track.id));

        grid.className = "market-item-grid";
        grid.replaceChildren();

        if (!savedTracks.length) {
            grid.textContent = "Your wishlist is empty.";
            return;
        }

        savedTracks.forEach(track => {
            const card = document.createElement("article");
            card.className = "market-card market-item-card";

            const icon = document.createElement("div");
            icon.className = "market-icon";
            icon.textContent = "🎵";

            const copy = document.createElement("div");
            copy.className = "market-item-copy";

            const title = document.createElement("h3");
            title.textContent = track.title;

            const artist = document.createElement("small");
            artist.textContent = track.artist || "Unknown artist";

            const price = document.createElement("strong");
            price.className = "market-price";
            price.textContent = `${track.price} pts`;

            copy.append(title, artist, price);

            const actions = document.createElement("div");
            actions.className = "market-music-actions";

            if (track.preview_url) {
                const previewButton = document.createElement("button");
                previewButton.type = "button";
                previewButton.textContent = "▶ Preview";
                previewButton.dataset.previewTrack = track.id;
                previewButton.dataset.previewUrl = track.preview_url;
                actions.appendChild(previewButton);
            }

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.textContent = "★ Wishlisted";
            removeButton.dataset.removeWishlist = track.id;

            actions.appendChild(removeButton);

            card.append(icon, copy, actions);
            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Wishlist error:", error);
        grid.textContent = error.message;
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

    const panelDescription = document.getElementById("topPanelDescription");

if (panelDescription && panelName === "market") {
    panelDescription.textContent = "Discover. Unlock. Customize.";
}

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




const favoriteButton = event.target.closest("[data-music-favorite]");

if (favoriteButton && event.currentTarget.contains(favoriteButton)) {
    const trackId = favoriteButton.dataset.musicFavorite;
    const wasFavorite = favoriteTrackIds.has(trackId);

    // Görünümü anında değiştir
    if (wasFavorite) {
        favoriteTrackIds.delete(trackId);
        favoriteButton.textContent = "♡ ";
    } else {
        favoriteTrackIds.add(trackId);
        favoriteButton.textContent = "♥";
    }

    favoriteButton.disabled = true;

    try {
        const response = await fetch("/api/music/favorites/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ track_id: trackId })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Favorite update failed.");
        }
        await loadOwnedMusic();

    } catch (error) {
        // İşlem başarısızsa eski duruma dön
        if (wasFavorite) {
            favoriteTrackIds.add(trackId);
            favoriteButton.textContent = "★";
        } else {
            favoriteTrackIds.delete(trackId);
            favoriteButton.textContent = "☆ ";
        }

        console.error("Favorite error:", error);

    } finally {
        favoriteButton.disabled = false;
    }

    return;
}



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
        if (selectedCategory === "wishlist") {
    await loadMarketWishlist();
}
        return;
    }

    const soundButton = event.target.closest("[data-market-play-sound]");
    if (soundButton && event.currentTarget.contains(soundButton)) {
        await playAmbientSound(soundButton.dataset.marketPlaySound);
        return;
    }


    const previewButton = event.target.closest("[data-preview-track]");
    if (previewButton && event.currentTarget.contains(previewButton)) {
        stopMarketPreview();

        marketPreviewAudio = new Audio(previewButton.dataset.previewUrl);
        marketPreviewAudio.volume = 0.7;

        marketPreviewAudio.play().catch(error => {
            console.error("Preview could not play:", error);
        });

        marketPreviewTimeout = setTimeout(stopMarketPreview, 25000);
        marketPreviewAudio.addEventListener("ended", stopMarketPreview, { once: true });
        return;
    }

    const wishlistButton = event.target.closest("[data-toggle-wishlist]");
    if (wishlistButton && event.currentTarget.contains(wishlistButton)) {
        wishlistButton.disabled = true;

        try {
            const response = await fetch("/api/music/wishlist/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    track_id: wishlistButton.dataset.toggleWishlist
                })
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || "Wishlist update failed.");
            }

            const isWishlisted = result.is_wishlisted;
            wishlistButton.dataset.wishlisted = String(isWishlisted);
            wishlistButton.textContent = isWishlisted ? "★ Wishlisted" : "♡ Wishlist";

        } catch (error) {
            console.error(error);
            document.getElementById("marketMusicMessage").textContent = error.message;
        } finally {
            wishlistButton.disabled = false;
        }
        return;
    }

const removeWishlistButton = event.target.closest("[data-remove-wishlist]");

if (removeWishlistButton && event.currentTarget.contains(removeWishlistButton)) {
    removeWishlistButton.disabled = true;

    try {
        const response = await fetch("/api/music/wishlist/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                track_id: removeWishlistButton.dataset.removeWishlist
            })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Could not remove track.");
        }

        await loadMarketWishlist();

    } catch (error) {
        console.error("Wishlist removal error:", error);
        removeWishlistButton.disabled = false;
    }

    return;
}

    const musicBuyButton = event.target.closest("[data-buy-music]");
    if (musicBuyButton && event.currentTarget.contains(musicBuyButton)) {
        if (musicBuyButton.disabled) return;

        musicBuyButton.disabled = true;
        musicBuyButton.textContent = "Processing...";

        try {
            const response = await fetch("/api/music/buy", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    track_id: musicBuyButton.dataset.buyMusic
                })
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.message || "Music purchase failed.");
            }

            updatePointsDisplay(result.points);
            musicBuyButton.textContent = "Owned ✓";

            await loadOwnedMusic();
            await loadMarketMusic();

            document.getElementById("marketMusicMessage").textContent =
                result.message || "Music purchased successfully.";

        } catch (error) {
            document.getElementById("marketMusicMessage").textContent = error.message;
            musicBuyButton.disabled = false;
            musicBuyButton.textContent = "Buy";
        }
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


document.addEventListener("click", async event => {
    // My Music / Favorites tab switching
    const tab = event.target.closest("[data-library-tab]");
    if (tab) {
        const selected = tab.dataset.libraryTab;

        document.querySelectorAll("[data-library-tab]").forEach(button => {
            button.classList.toggle("active", button === tab);
        });

        const myMusic = document.getElementById("myMusicList");
        const favorites = document.getElementById("favoritesList");

        if (myMusic) myMusic.hidden = selected !== "my-music";
        if (favorites) favorites.hidden = selected !== "favorites";

        const ambientFavorites = document.getElementById("ambientFavoritesList");

if (ambientFavorites) {
    ambientFavorites.hidden = selected !== "favorites";
}
        return;
    }
// Play a purchased track
const playButton = event.target.closest("[data-play-owned-track]");

if (playButton) {
    const track = {
        audio_url: playButton.dataset.audioUrl,
        title: playButton.dataset.trackTitle,
        artist: playButton.dataset.trackArtist
    };

    if (!track.audio_url) {
        console.error("Track audio URL is missing.");
        return;
    }

    await playOwnedTrack(track);
    return;
}

    // Toggle a purchased track's favorite status
    const favoriteButton = event.target.closest("[data-toggle-favorite]");
    if (favoriteButton) {
    const wasFavorite = favoriteButton.dataset.favorite === "true";

    // Update the button immediately
    favoriteButton.dataset.favorite = String(!wasFavorite);
    favoriteButton.textContent = !wasFavorite ? " ♥" : " ♡";

    updateFavoriteTracksUI(favoriteButton, !wasFavorite);

    try {
        const response = await fetch("/api/music/favorites/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                track_id: favoriteButton.dataset.toggleFavorite
            })
        });

        const result = await response.json();

           if (!response.ok || !result.success) {
            throw new Error(result.message || "Favorite update failed.");
      }



        } catch (error) {
        // Restore previous state if the request fails
        favoriteButton.dataset.favorite = String(wasFavorite);
        favoriteButton.textContent = wasFavorite ? " ♥" : " ♡";
        console.error(error);
    }
}
});

// Load the user's purchased music when the page starts
loadOwnedMusic();

document.addEventListener("navigation:panel-open", event => {
    if (event.detail.panelName !== "market") {
        stopMarketPreview();
    }
});
