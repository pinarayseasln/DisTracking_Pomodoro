const navButtons = document.querySelectorAll(".nav-action");
const topPanel = document.getElementById("topPanel");
const topPanelTitle = document.getElementById("topPanelTitle");
const topPanelDescription = document.getElementById("topPanelDescription");

let activePanelName = null;

export function isActivePanel(panelName) {
    return activePanelName === panelName;
}

export function activatePanel(panelName, panel) {
    activePanelName = panelName;
    topPanel.dataset.panel = panelName;

    navButtons.forEach(button => {
        button.classList.toggle("active", button.dataset.panel === panelName);
    });

    topPanelTitle.textContent = panel.title;
    topPanelDescription.textContent = panel.description;
}

export function clearActivePanel() {
    activePanelName = null;
    navButtons.forEach(button => button.classList.remove("active"));
}

export function setPanelVisible(isVisible) {
    topPanel.hidden = !isVisible;
}
