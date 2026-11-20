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
