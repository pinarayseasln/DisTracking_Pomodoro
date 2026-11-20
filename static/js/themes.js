// ===== Site theme =====

function applySiteTheme(theme) {
    document.body.dataset.theme = theme;

    const darkThemes = ["woods", "neon", "burgundy"];

    document.body.dataset.cityMode =
        darkThemes.includes(theme) ? "dark" : "light";

    localStorage.setItem("disTheme", theme);
}

const savedTheme = localStorage.getItem("disTheme") || "woods";
applySiteTheme(savedTheme);

const topPanelContent = document.getElementById("topPanelContent");

topPanelContent.addEventListener("click", (event) => {
    const themeButton = event.target.closest("[data-theme-choice]");
    if (!themeButton || !event.currentTarget.contains(themeButton)) return;

    const selectedTheme = themeButton.dataset.themeChoice;
    applySiteTheme(selectedTheme);

    topPanelContent.querySelectorAll(".theme-card").forEach(card => {
        const isSelected = card.dataset.themeChoice === selectedTheme;

        card.classList.toggle("selected", isSelected);
        card.querySelector("small").textContent =
            isSelected ? "Currently selected" : "Select theme";
    });
});
