// ===== Pomodoro completion modal =====

const completionModal = document.getElementById("completionModal");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalContinueBtn = document.getElementById("modalContinueBtn");

function openCompletionModal(pointsEarned, totalPoints) {
    document.getElementById("modalTitle").textContent = "Great work!";
    document.getElementById("modalDescription").textContent =
        "You completed your focus session.";

    document.getElementById("earnedPoints").textContent = pointsEarned;
    document.getElementById("modalTotalPoints").textContent = totalPoints;

    completionModal.classList.add("show");
}

function closeCompletionModal() {
    completionModal.classList.remove("show");
}

modalCloseBtn.addEventListener("click", closeCompletionModal);
modalContinueBtn.addEventListener("click", closeCompletionModal);

completionModal.addEventListener("click", (event) => {
    if (event.target === completionModal) {
        closeCompletionModal();
    }
});

document.addEventListener("pomodoro:completion-modal-open", (event) => {
    const { pointsEarned, totalPoints } = event.detail;
    openCompletionModal(pointsEarned, totalPoints);
});
