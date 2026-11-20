import { loadCityState, resetCityMapPosition } from "./city.js";

const cityMapWorld = document.getElementById("cityMapWorld");
const cityIslandName = document.getElementById("cityIslandName");
const cityMapImage = cityMapWorld.querySelector("img");
const cityFrameImage = document.getElementById("cityFrameImage");
const openCityBtn = document.getElementById("openCityBtn");
const closeCityBtn = document.getElementById("closeCityBtn");
const cityOverlay = document.getElementById("cityOverlay");
const cityPreviewImage = document.querySelector(".city-preview-cover");
const activeCityNameLabel = document.getElementById("activeCityName");
const cityAssetBase = new URL(".", cityMapImage.src);
const cityOptions = {
    "Green Valley": { image: "green_valley.png", frame: "city_frame_ivy.png" },
    "Crystal Village": { image: "Cyristal_Village_HD.png", frame: "cyristal_village_transparent.png" },
    "Dark Thorn": { image: "Dark_Thorn_village_HD.png", frame: "dark_thorn_transparent.png" }
};
let activeCityName = "Green Valley";

function cityAsset(filename) {
    return new URL(encodeURIComponent(filename), cityAssetBase).href;
}

function applyCity(name, { open = false, persist = false } = {}) {
    const city = cityOptions[name] ? name : "Green Valley";
    const assets = cityOptions[city];
    const image = cityAsset(assets.image);
    const frame = cityAsset(assets.frame);

    activeCityName = city;
    cityIslandName.textContent = city;
    activeCityNameLabel.textContent = city;
    cityPreviewImage.src = image;
    cityPreviewImage.alt = `${city} city`;
    cityMapImage.src = image;
    cityMapImage.alt = city;
    cityFrameImage.src = frame;
    cityOverlay.classList.toggle("island-map", city !== "Green Valley");
    cityOverlay.dataset.island = city.toLowerCase().replaceAll(" ", "-");
    resetCityMapPosition();
    cityOverlay.hidden = !open;

    if (persist) localStorage.setItem("disActiveCity", city);
    if (open) loadCityState(city);
}

applyCity(localStorage.getItem("disActiveCity") || "Green Valley");

openCityBtn.addEventListener("click", () => {
    applyCity(activeCityName, { open: true });
});

const islandPreviewGrid = document.querySelector(".island-preview-grid");
islandPreviewGrid.addEventListener("click", event => {
    const card = event.target.closest(".island-preview-card");
    if (!card || !islandPreviewGrid.contains(card)) return;

    applyCity(card.dataset.islandName, { open: true, persist: true });
});
closeCityBtn.addEventListener("click", () => {
    cityOverlay.hidden = true;
});

cityOverlay.addEventListener("click", event => {
    if (event.target === cityOverlay) {
        cityOverlay.hidden = true;
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        cityOverlay.hidden = true;
    }
});
