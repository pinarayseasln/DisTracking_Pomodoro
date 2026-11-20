const topPanelContent = document.getElementById("topPanelContent");


document.addEventListener("navigation:panel-open", (event) => {
    const { panelName, panel } = event.detail;

        if (panelName === "themes") {
    const currentTheme = document.body.dataset.theme;

    const themes = [
        { id: "woods", name: "Whispering Woods", image: "whispering-woods.png" },
        { id: "neon", name: "Neon Afterglow", image: "neon-afterglow.png" },
        { id: "sakura-coast", name: "Sakura Coast", image: "sakura-coast.png" },
        { id: "burgundy", name: "Burgundy Royale", image: "burgundy-royale.png" }
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
