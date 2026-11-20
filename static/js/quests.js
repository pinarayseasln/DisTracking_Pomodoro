// ===== DAILY QUESTS =====

const topPanelContent = document.getElementById("topPanelContent");
let quests = [];
let activeQuestId = topPanelContent.dataset.activeQuestId
    ? Number(topPanelContent.dataset.activeQuestId)
    : null;

function setActiveQuest(questId) {
    activeQuestId = questId;
    if (questId === null || questId === undefined) {
        delete topPanelContent.dataset.activeQuestId;
    } else {
        topPanelContent.dataset.activeQuestId = String(questId);
    }
}

async function loadQuests() {
    try {
        const response = await fetch("/api/quests");
        const data = await response.json();

        if (!data.success) throw new Error("Could not load quests.");

        quests = data.quests;
        renderQuests();
    } catch (error) {
        console.error(error);
        const list = document.getElementById("todoList");
        if (list) list.textContent = "Could not load quests.";
    }
}


function renderQuests() {
    const list = document.getElementById("todoList");
    const empty = document.getElementById("todoEmpty");

    if (!list || !empty) return;

    list.innerHTML = "";
    empty.hidden = quests.length > 0;

    const categories = {
        study: { name: "STUDY", icon: "📚" },
        work: { name: "WORK", icon: "💻" },
        personal: { name: "PERSONAL", icon: "🌱" },
        health: { name: "HEALTH", icon: "💪" },
        creative: { name: "CREATIVE", icon: "🎨" }
    };

    quests.forEach(quest => {
        const completed =
            quest.completed_pomodoros >= quest.required_pomodoros;
        const active = activeQuestId === quest.id;
        const category = categories[quest.category] ||
            { name: quest.category.toUpperCase(), icon: "✨" };

        const item = document.createElement("div");
        item.className = `todo-item ${completed ? "completed" : ""} ${active ? "active" : ""}`;

        const top = document.createElement("div");
        top.className = "quest-card-top";

        const categoryBadge = document.createElement("span");
        categoryBadge.className = "quest-category";
        categoryBadge.textContent = `${category.icon} ${category.name}`;

        const reward = document.createElement("span");
        reward.className = "quest-reward";
        reward.textContent = completed ? "✓ COMPLETED" : "+10 XP";

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.textContent = "×";
        deleteButton.className = "todo-delete";
        deleteButton.setAttribute("aria-label", "Delete quest");

        top.append(categoryBadge, reward, deleteButton);

        const heading = document.createElement("div");
        heading.className = "todo-task-text";
        heading.textContent = quest.task_text;

        const progressInfo = document.createElement("div");
        progressInfo.className = "quest-progress-info";

        const progressText = document.createElement("span");
        progressText.textContent =
            `${quest.completed_pomodoros} / ${quest.required_pomodoros} Pomodoros`;

        const percentage = document.createElement("span");
        percentage.textContent =
            `${Math.round((quest.completed_pomodoros / quest.required_pomodoros) * 100)}%`;

        progressInfo.append(progressText, percentage);

        const progressBar = document.createElement("progress");
        progressBar.max = quest.required_pomodoros;
        progressBar.value = quest.completed_pomodoros;

        const focusButton = document.createElement("button");
        focusButton.type = "button";
        focusButton.className = "quest-focus-button";
        focusButton.textContent = completed
            ? "✓ Quest completed"
            : active
                ? "🎯 Currently focusing"
                : "Focus on this quest →";
        focusButton.disabled = completed;

        focusButton.addEventListener("click", () => {
            setActiveQuest(quest.id);
            renderQuests();
        });

        deleteButton.addEventListener("click", async () => {
            if (deleteButton.disabled) return;
            if (!confirm("Delete this quest?")) return;

            const originalLabel = deleteButton.textContent;
            const failureMessage = "Quest could not be deleted. Please try again.";
            let deleted = false;
            deleteButton.disabled = true;
            deleteButton.textContent = "Deleting...";

            try {
                const response = await fetch(`/api/quests/${quest.id}`, {
                    method: "DELETE"
                });

                let data = null;
                try {
                    data = await response.json();
                } catch {
                    // Use the fallback below when the server response is not JSON.
                }

                if (!response.ok || !data?.success) {
                    alert(data?.error || data?.message || failureMessage);
                    return;
                }

                deleted = true;
            } catch {
                alert(failureMessage);
            } finally {
                if (!deleted) {
                    deleteButton.disabled = false;
                    deleteButton.textContent = originalLabel;
                }
            }

            if (!deleted) return;
            if (activeQuestId === quest.id) setActiveQuest(null);
            await loadQuests();
        });

        item.append(
            top,
            heading,
            progressInfo,
            progressBar,
            focusButton
        );

        list.appendChild(item);
    });
}

// Quest oluştur
topPanelContent.addEventListener("submit", async (event) => {
    if (event.target.id !== "todoForm") return;

    event.preventDefault();

    const taskText = document.getElementById("todoInput").value.trim();
    const category = document.getElementById("todoCategory").value;
    const requiredPomodoros =
        Number(document.getElementById("requiredPomodoros").value);

    if (!taskText || !category) return;

    try {
        const response = await fetch("/api/quests", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task_text: taskText,
                category: category,
                required_pomodoros: requiredPomodoros
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Quest could not be created.");
        }

        event.target.reset();
        await loadQuests();

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
});

document.addEventListener("quests:load", () => {
    loadQuests();
});

document.addEventListener("pomodoro:quest-session-state", (event) => {
    setActiveQuest(event.detail.questId);
    renderQuests();
});

document.addEventListener("pomodoro:quest-session-completed", (event) => {
    event.detail.completion = refreshAfterPomodoro(event.detail.questId);
});

async function refreshAfterPomodoro(questId) {
    await loadQuests();
    const completedQuest = quests.find(quest => quest.id === questId);
    if (!completedQuest || completedQuest.completed_pomodoros >= completedQuest.required_pomodoros) {
        setActiveQuest(null);
        renderQuests();
    }
}
