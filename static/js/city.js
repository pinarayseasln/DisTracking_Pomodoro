const cityMapWorld = document.getElementById("cityMapWorld");
const cityMapViewport = document.getElementById("cityMapViewport");
const cityRebuildPanel = document.getElementById("cityRebuildPanel");
const cityDecorationWorld = document.getElementById("cityDecorationWorld");
const cityItemNames = {
    weed: "Weed",
    debris: "Debris",
    wood: "Wood",
    brick: "Brick",
    weed_tool: "Weed Tool",
    shovel: "Shovel",
};

let activeRebuildCity = "green-valley";
let rebuildRequestPending = false;

let mapDragging = false;
let mapStartX = 0;
let mapStartY = 0;
let mapOffsetX = 0;
let mapOffsetY = 0;

export function resetCityMapPosition() {
    mapOffsetX = 0;
    mapOffsetY = 0;
    if (cityMapWorld) {
        cityMapWorld.style.transform = "translate(-50%, -50%)";
    }
}

if (cityMapWorld && cityMapViewport) {
    cityMapViewport.addEventListener("pointerdown", event => {
        if (event.target.closest(".city-map-label, .city-interactive")) return;
        if (event.pointerType === "mouse" && event.button !== 0) return;

        event.preventDefault();
        mapDragging = true;
        mapStartX = event.clientX - mapOffsetX;
        mapStartY = event.clientY - mapOffsetY;

        cityMapViewport.setPointerCapture(event.pointerId);
    });

    cityMapViewport.addEventListener("pointermove", event => {
        if (!mapDragging) return;

        mapOffsetX = event.clientX - mapStartX;
        mapOffsetY = event.clientY - mapStartY;

        const maxX = Math.max(
            0,
            (cityMapWorld.offsetWidth - cityMapViewport.clientWidth) / 2
        );
        const maxY = Math.max(
            0,
            (cityMapWorld.offsetHeight - cityMapViewport.clientHeight) / 2
        );

        mapOffsetX = Math.max(-maxX, Math.min(maxX, mapOffsetX));
        mapOffsetY = Math.max(-maxY, Math.min(maxY, mapOffsetY));

        cityMapWorld.style.transform =
            `translate(calc(-50% + ${mapOffsetX}px), calc(-50% + ${mapOffsetY}px))`;
    });

    function stopMapDragging() {
        mapDragging = false;
    }

    cityMapViewport.addEventListener("pointerup", stopMapDragging);
    cityMapViewport.addEventListener("pointercancel", stopMapDragging);
    cityMapViewport.addEventListener("lostpointercapture", stopMapDragging);
}

export function updateCityStat(stat, value) {
    const item = document.querySelector(`.city-stat-item[data-stat="${stat}"]`);
    if (!item) return;

    const numericValue = Number(value);
    const safeValue = Math.max(0, Math.min(100, Number.isFinite(numericValue) ? numericValue : 0));
    const valueLabel = item.querySelector(".city-stat-value");
    const meterFill = item.querySelector(".city-stat-meter i");

    if (valueLabel) {
        valueLabel.textContent = stat === "population"
            ? String(Math.round(safeValue))
            : `${Math.round(safeValue)}%`;
    }

    if (meterFill) {
        meterFill.style.width = `${safeValue}%`;
    }
}

function formatRequirements(requirements, tools) {
    const lines = [
        ...Object.entries(requirements).map(([id, quantity]) => `${quantity} ${cityItemNames[id] || id}`),
        ...Object.entries(tools).map(([id]) => `Requires ${cityItemNames[id] || id}`),
    ];
    return lines.join(" · ");
}

function renderDecorationSpots(state) {
    cityDecorationWorld.replaceChildren();
    cityDecorationWorld.hidden = state.stage < state.stages;
    if (cityDecorationWorld.hidden) return;

    const placedBySlot = new Map(state.decorations.map(item => [item.slot_id, item.decoration_id]));
    const icons = { fountain: "⛲", tree: "🌳", flower_bed: "🌷" };
    const names = { fountain: "Fountain", tree: "Tree", flower_bed: "Flower Bed" };

    Object.entries(state.slots).forEach(([slotId, slot]) => {
        const decorationId = placedBySlot.get(slotId);
        const spot = document.createElement(decorationId ? "span" : "button");
        spot.className = decorationId
            ? "city-decoration-placement"
            : "city-decoration-slot city-interactive";
        spot.style.left = `${slot.x}%`;
        spot.style.top = `${slot.y}%`;
        spot.dataset.citySlot = slotId;
        spot.setAttribute("aria-label", decorationId
            ? `${names[decorationId]} in ${slot.label}`
            : `Place decoration in ${slot.label}`);
        if (decorationId) {
            spot.textContent = icons[decorationId] || "✿";
            spot.title = `${names[decorationId]} · ${slot.label}`;
        } else {
            spot.type = "button";
            spot.textContent = "+";
            spot.title = slot.label;
        }
        cityDecorationWorld.append(spot);
    });
}

function renderCityState(state) {
    cityMapWorld.dataset.rebuildStage = String(state.stage);
    document.getElementById("cityRebuildStage").textContent = state.stage < state.stages
        ? `Stage ${state.stage + 1} of ${state.stages}`
        : "All stages complete";

    const taskTitle = document.getElementById("cityTaskTitle");
    const taskRequirements = document.getElementById("cityTaskRequirements");
    const inventory = document.getElementById("cityTaskInventory");
    const completeButton = document.getElementById("completeCityStage");
    const decorationPicker = document.getElementById("cityDecorationPicker");
    const decorationChoice = document.getElementById("cityDecorationChoice");
    const completedIds = new Set(state.completed_tasks.map(task => task.task_id));

    if (state.current_task) {
        const task = state.current_task;
        taskTitle.textContent = task.name;
        taskRequirements.textContent = formatRequirements(task.requirements, task.tools);
        const allRequirements = { ...task.requirements, ...task.tools };
        inventory.replaceChildren();
        let canComplete = true;
        Object.entries(allRequirements).forEach(([id, required]) => {
            const owned = state.inventory[id] || 0;
            const line = document.createElement("span");
            line.className = owned >= required ? "has-stock" : "needs-stock";
            line.textContent = `${cityItemNames[id] || id}: ${owned}/${required}`;
            inventory.append(line);
            if (owned < required) canComplete = false;
        });
        completeButton.hidden = false;
        completeButton.dataset.requirementsMet = String(canComplete);
        completeButton.disabled = !canComplete || rebuildRequestPending;
        completeButton.textContent = "Complete stage";
    } else {
        taskTitle.textContent = "Shelter rebuilt!";
        taskRequirements.textContent = "Choose an owned decoration, then select an empty spot on the map.";
        inventory.replaceChildren();
        completeButton.hidden = true;
    }

    decorationPicker.hidden = state.stage < state.stages;
    decorationChoice.replaceChildren(new Option("Choose owned decoration", ""));
    [
        ["fountain", "Fountain"],
        ["tree", "Tree"],
        ["flower_bed", "Flower Bed"],
    ].forEach(([id, name]) => {
        const quantity = state.inventory[id] || 0;
        if (quantity < 1) return;
        decorationChoice.append(new Option(`${name} (${quantity})`, id));
    });
    renderDecorationSpots(state);

    const completedList = document.getElementById("cityCompletedTasks");
    if (completedList) {
        completedList.textContent = `${completedIds.size}/${state.stages} tasks complete`;
    }
}

export async function loadCityState(cityName = "Green Valley") {
    activeRebuildCity = cityName.toLowerCase().replaceAll(" ", "-");
    const isGreenValley = activeRebuildCity === "green-valley";
    cityRebuildPanel.hidden = !isGreenValley;
    if (!isGreenValley) {
        delete cityMapWorld.dataset.rebuildStage;
        cityDecorationWorld.replaceChildren();
        cityDecorationWorld.hidden = true;
        return;
    }

    const message = document.getElementById("cityRebuildMessage");
    message.textContent = "";
    try {
        const response = await fetch(`/api/cities/${activeRebuildCity}/rebuild`);
        const state = await response.json();
        if (!response.ok || !state.success) {
            throw new Error(state.message || "City progress could not be loaded.");
        }
        renderCityState(state);
    } catch (error) {
        message.textContent = error.message;
    }
}

document.getElementById("completeCityStage").addEventListener("click", async event => {
    if (rebuildRequestPending) return;
    rebuildRequestPending = true;
    event.currentTarget.disabled = true;
    const message = document.getElementById("cityRebuildMessage");
    message.textContent = "Working on the city…";
    try {
        const response = await fetch(`/api/cities/${activeRebuildCity}/rebuild/complete`, {
            method: "POST",
        });
        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(result.message || "This stage could not be completed.");
        }
        await loadCityState("Green Valley");
        message.textContent = result.message;
    } catch (error) {
        message.textContent = error.message;
    } finally {
        rebuildRequestPending = false;
        const button = document.getElementById("completeCityStage");
        if (!button.hidden) button.disabled = button.dataset.requirementsMet !== "true";
    }
});

cityDecorationWorld.addEventListener("click", async event => {
    const spot = event.target.closest("[data-city-slot]");
    if (!spot || !event.currentTarget.contains(spot) || spot.tagName !== "BUTTON") return;
    const decorationId = document.getElementById("cityDecorationChoice").value;
    const message = document.getElementById("cityRebuildMessage");
    if (!decorationId) {
        message.textContent = "Buy a decoration in the Market and choose it above first.";
        return;
    }

    spot.disabled = true;
    try {
        const response = await fetch(`/api/cities/${activeRebuildCity}/decorations/place`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ slot_id: spot.dataset.citySlot, decoration_id: decorationId }),
        });
        const result = await response.json();
        if (!response.ok || !result.success) {
            throw new Error(result.message || "Decoration could not be placed.");
        }
        await loadCityState("Green Valley");
        message.textContent = result.message;
    } catch (error) {
        message.textContent = error.message;
        spot.disabled = false;
    }
});
