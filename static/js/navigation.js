// ===== Top panel navigation =====

import {
    activatePanel,
    clearActivePanel,
    isActivePanel,
    setPanelVisible
} from "./ui-state.js";

const navButtons = document.querySelectorAll(".nav-action");
const closeTopPanel = document.getElementById("closeTopPanel");

const panelInfo = {
    todo: {
        title: "To-do List",
        description: "Organize your tasks",
        content: "Your tasks will appear here."
    },
    themes: {
        title: "Themes",
        description: "Choose your workspace atmosphere",
        content: "Your themes will appear here."
    },
    friends: {
        title: "Friends & Group",
        description: "Connect and focus together",
        content: "Your friends and groups will appear here."
    },
    market: {
        title: "Market",
        description: "Build your productivity world",
        content: "Available items will appear here."
    },
    profile: {
        title: "Profile",
        description: "Your personal productivity space",
        content: "Your profile information will appear here."
    }
};

navButtons.forEach(button => {
    button.addEventListener("click", () => {
        const panelName = button.dataset.panel;

        if (isActivePanel(panelName)) {
            setPanelVisible(false);
            clearActivePanel();
            return;
        }

        const panel = panelInfo[panelName];
        activatePanel(panelName, panel);

        document.dispatchEvent(new CustomEvent("navigation:panel-open", {
            detail: { panelName, panel }
        }));
        setPanelVisible(true);
    });
});

closeTopPanel.addEventListener("click", () => {
    setPanelVisible(false);
    clearActivePanel();
});
