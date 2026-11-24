const topPanelContent = document.getElementById("topPanelContent");


document.addEventListener("navigation:panel-open", (event) => {
    const { panelName, panel } = event.detail;

        if (panelName === "themes") {
    const currentTheme = document.body.dataset.theme;


const themes = [
    { id: "woods", name: "Whispering Woods", image: "whispering-woods.png" },
    { id: "neon", name: "Neon Afterglow", image: "neon-afterglow.png" },
    { id: "sakura-coast", name: "Sakura Coast", image: "sakura-coast.png" },
    { id: "burgundy", name: "Burgundy Royale", image: "burgundy-royale.png" },

    { id: "billiard-lounge", name: "Billiard Lounge", image: "Billiard Lounge.png" },
    { id: "camping-in-the-forest", name: "Camping in the Forest", image: "Camping in the forest.png" },
    { id: "clear-terrain", name: "Clear Terrain", image: "Clear Terrain.jpeg" },
    { id: "cozy-room", name: "Cozy Room", image: "Cozy Room.png" },
    { id: "dawn-sailboat", name: "Dawn Sailboat", image: "Dawn Sailboat.png" },
    { id: "death-flower", name: "Death Flower", image: "Death Flower.jpeg" },
    { id: "faithful-love", name: "Faithful Love", image: "Faithful Love.jpeg" },

    { id: "howls-castle", name: "Howl's Moving Castle", image: "Howl's Moving Castle.jpeg" },
    { id: "infinite-valley", name: "Infinite Valley", image: "infinite valley.png" },
    { id: "iron-man", name: "Iron Man", image: "Iron Man.jpeg" },
    { id: "japan-streets", name: "Japan Streets", image: "Japan Streets.png" },
    { id: "jinx-ekko", name: "Jinx & Ekko", image: "jinx & Ekko .jpeg" },
    { id: "joker", name: "Joker", image: "Joker.jpeg" },
     { id: "golden-hour", name: "Golden Hour", image: "Golden Hour.png" },
    { id: "lake-alps", name: "Lake of the Alps", image: "Lake of the Alps.png" },
    { id: "lavender-villa", name: "Lavender Villa", image: "Lavender Villa.png" },
    { id: "mcqueen", name: "McQueen", image: "McQueen.jpeg" },
    { id: "metro-tunnel", name: "Metro Tunnel", image: "Metro Tunnel.png" },
    { id: "northern-lights", name: "Northern Lights", image: "northern lights.jpeg" },
    { id: "on-the-lake", name: "On the Lake", image: "On the Lake.jpeg" },
    { id: "optimus", name: "Optimus", image: "Optimus.jpeg" },
    { id: "porsche", name: "Porsche", image: "Porsche.jpeg" },
    { id: "purple-dream", name: "Purple Dream", image: "Purple Dream.jpeg" },
    { id: "roman-ruins", name: "Roman Ruins", image: "Roman Ruins.png" },
    { id: "seaside-vista", name: "Seaside Vista", image: "Seaside vista.jpeg" },
    { id: "ghost", name: "Simon 'Ghost' Riley", image: "Simon 'Ghost' Riley.jpeg" },
    { id: "spiderman", name: "Spiderman", image: "Spiderman.jpeg" },
    { id: "sunset-alps", name: "Sunset of Alps", image: "Sunset of the Alps.png" },
   { id: "place-born", name: "The Place Where I was Born", image: "The Place Where I was Born.jpeg" },
    { id: "thomas-shelby", name: "Thomas Shelby", image: "Thomas Shelby.jpeg" },
    { id: "tulip-twilight", name: "Tulip Twilight", image: "Tulip Twilight.jpeg" },
    { id: "ying-yang", name: "Ying & Yang", image: "Ying & Yang.jpeg" }
];

    topPanelContent.innerHTML = `
        <div class="theme-grid">
            ${themes.map(theme => `
                <button
                    type="button"
                    class="theme-card ${currentTheme === theme.id ? "selected" : ""}"
                    data-theme-choice="${theme.id}"
                >
                    <img
                        src="/static/backgrounds/${theme.image}"
                        alt="${theme.name}"
                    >
                    <span>${theme.name}</span>
                    <small>${currentTheme === theme.id ? "Currently selected" : "Select theme"}</small>
                </button>
            `).join("")}
        </div>
    `;


} else if (panelName === "todo") {
    topPanelContent.innerHTML = `
        <div class="todo-panel">
            <form id="todoForm" class="todo-form">
                <input
                    type="text"
                    id="todoInput"
                    placeholder="What needs to get done?"
                    maxlength="100"
                    required
                >

               <select id="todoCategory" required>
    <option value="">Choose category</option>
    <option value="study">📚 Study</option>
    <option value="work">💻 Work</option>
    <option value="personal">🌱 Personal</option>
    <option value="health">💪 Health</option>
    <option value="creative">🎨 Creative</option>
</select>

<div class="pomodoro-goal-field">
    <label for="requiredPomodoros">Pomodoro goal</label>
    <select id="requiredPomodoros" required>
        ${Array.from({length: 10}, (_, i) =>
            `<option value="${i + 1}">${i + 1} Pomodoro${i ? "s" : ""}</option>`
        ).join("")}
    </select>
</div>


                <button type="submit">＋ Add Quest</button>
            </form>

            <div class="todo-list" id="todoList"></div>

            <p class="todo-empty" id="todoEmpty" hidden>
                No quests yet. Create your first daily quest!
            </p>
        </div>
    `;
    document.dispatchEvent(new Event("quests:load"));

} else {
    topPanelContent.textContent = panel.content;
}

});
