const focusResetScreen = document.getElementById("focusResetScreen");
const lostFocusBtn = document.getElementById("lostFocusBtn");
const taskChoiceStep = document.getElementById("taskChoiceStep");
const taskResultStep = document.getElementById("taskResultStep");
const taskFlowError = document.getElementById("taskFlowError");
const taskCompleteMessage = document.getElementById("taskCompleteMessage");
let selectedNeed = null;
let selectedMaxDuration = 3;
let currentRecommendedTask = null;
let recommendedTaskIds = [];

lostFocusBtn.addEventListener("click", () => {
    document.dispatchEvent(new Event("focus-tasks:stop-timer"));
    selectedNeed = null;
    currentRecommendedTask = null;
    recommendedTaskIds = [];
    taskChoiceStep.hidden = false;
    taskResultStep.hidden = true;
    taskFlowError.hidden = true;
    document.querySelectorAll("[data-feeling]").forEach(item => {
        item.classList.remove("is-selected");
        item.setAttribute("aria-pressed", "false");
    });
    focusResetScreen.showModal();
});

document.getElementById("closeFocusReset").addEventListener("click", () => focusResetScreen.close());
document.getElementById("returnToTimer").addEventListener("click", () => focusResetScreen.close());

document.querySelectorAll("[data-feeling]").forEach(option => {
    option.addEventListener("click", () => {
        selectedNeed = option.dataset.feeling;
        document.querySelectorAll("[data-feeling]").forEach(item => {
            item.classList.remove("is-selected");
            item.setAttribute("aria-pressed", "false");
        });
        option.classList.add("is-selected");
        option.setAttribute("aria-pressed", "true");
    });
});

document.querySelectorAll("[data-reset-duration]").forEach(option => {
    option.addEventListener("click", () => {
        selectedMaxDuration = Number(option.dataset.resetDuration);
        document.querySelectorAll("[data-reset-duration]").forEach(item => {
            item.classList.remove("is-selected");
            item.setAttribute("aria-pressed", "false");
        });
        option.classList.add("is-selected");
        option.setAttribute("aria-pressed", "true");
    });
});

async function requestRecommendedTask(excludeCurrent = false) {
    taskFlowError.hidden = true;
    taskCompleteMessage.hidden = true;
    if (!selectedNeed) {
        taskFlowError.textContent = "Choose what you need first.";
        taskFlowError.hidden = false;
        return;
    }
    if (excludeCurrent && currentRecommendedTask) recommendedTaskIds.push(currentRecommendedTask.id);
    const button = document.getElementById("getTaskBtn");
    button.disabled = true;
    button.textContent = "Finding a task…";
    try {
        const response = await fetch("/api/tasks/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ need: selectedNeed, max_duration: selectedMaxDuration, exclude_ids: recommendedTaskIds })
        });
        const payload = await response.json();
        if (!response.ok || !payload.success) throw new Error(payload.error || "Could not find a task.");
        currentRecommendedTask = payload.task;
        document.getElementById("recommendedCategory").textContent = payload.category_name;
        document.getElementById("recommendedTitle").textContent = payload.task.title;
        document.getElementById("recommendedDescription").textContent = payload.task.description;
        document.getElementById("recommendedDuration").textContent = `${payload.task.duration} min`;
        document.getElementById("recommendedXp").textContent = `+${payload.task.xp} XP`;
        document.getElementById("completeTaskBtn").disabled = false;
        document.getElementById("completeTaskBtn").textContent = "Complete task";
        taskChoiceStep.hidden = true;
        taskResultStep.hidden = false;
    } catch (error) {
        taskFlowError.textContent = error.message;
        taskFlowError.hidden = false;
    } finally {
        button.disabled = false;
        button.innerHTML = 'Suggest a task <span aria-hidden="true">→</span>';
    }
}

document.getElementById("getTaskBtn").addEventListener("click", () => requestRecommendedTask(false));
document.getElementById("tryAnotherTaskBtn").addEventListener("click", () => requestRecommendedTask(true));
document.getElementById("chooseTaskAgainBtn").addEventListener("click", () => {
    taskResultStep.hidden = true;
    taskChoiceStep.hidden = false;
    taskCompleteMessage.hidden = true;
});

document.getElementById("completeTaskBtn").addEventListener("click", async event => {
    if (!currentRecommendedTask) return;
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = "Saving…";
    taskCompleteMessage.hidden = true;
    try {
        const response = await fetch("/api/tasks/complete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: currentRecommendedTask.id })
        });
        const payload = await response.json();
        if (!response.ok || !payload.success) throw new Error(payload.error || "Could not save this task.");
        document.dispatchEvent(new CustomEvent("focus-tasks:points-updated", { detail: { points: payload.points } }));
        button.textContent = "Completed ✓";
        taskCompleteMessage.textContent = `You earned ${payload.earned_xp} XP. Nice work!`;
        taskCompleteMessage.hidden = false;
    } catch (error) {
        button.disabled = false;
        button.textContent = "Complete task";
        taskCompleteMessage.textContent = error.message;
        taskCompleteMessage.hidden = false;
    }
});
