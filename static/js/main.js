// Preserve the app's previous startup order. Each imported module is evaluated
// once by the ES module loader, including shared dependencies such as api.js.
import "./panel-content.js";
import "./api.js";
import "./pomodoro.js";
import "./focus-tasks.js";
import "./ambient-player.js";
import "./themes.js";
import "./completion-modal.js";
import "./quests.js";
import "./navigation.js";
import "./panel-actions.js";
import "./market.js";


// Close top panel when clicking outside
document.addEventListener("click", event => {
    const topPanel = document.getElementById("topPanel");

    if (!topPanel || topPanel.hidden) return;

    // Keep panel open when clicking inside it or on navigation buttons
    if (
        event.target.closest("#topPanel") ||
        event.target.closest(".top-actions")
    ) {
        return;
    }

    topPanel.hidden = true;

    // Remove active state from navigation buttons
    document.querySelectorAll(".nav-action.active").forEach(button => {
        button.classList.remove("active");
    });

    // Hide market balance if it is visible
    const marketBalance = document.getElementById("marketBalance");
    if (marketBalance) marketBalance.hidden = true;
});
