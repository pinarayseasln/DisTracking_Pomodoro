
from flask import Blueprint, jsonify, request, render_template

from models.quest_model import (
    create_quest as create_quest_model,
    get_quests as get_quests_model,
    delete_quest as delete_quest_model
)

from models.task_model import complete_task as complete_task_model

from task_library import CATEGORIES, get_catalog, get_task
from task_strategies import TaskRecommendationContext


tasks_bp = Blueprint("tasks", __name__)


# Daily Quest oluştur
@tasks_bp.route('/api/quests', methods=['POST'])
def create_quest():
    payload = request.get_json(silent=True) or {}

    task_text = payload.get("task_text", "").strip()
    category = payload.get("category", "").strip()

    try:
        required_pomodoros = int(payload.get("required_pomodoros"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid Pomodoro target."
        }), 400

    if not task_text or not category:
        return jsonify({
            "success": False,
            "error": "Task and category are required."
        }), 400

    if not 1 <= required_pomodoros <= 10:
        return jsonify({
            "success": False,
            "error": "Pomodoro target must be between 1 and 10."
        }), 400

    quest_id = create_quest_model(
        task_text,
        category,
        required_pomodoros
    )

    return jsonify({
        "success": True,
        "quest_id": quest_id
    })


# Daily Quest listesini getir
@tasks_bp.route('/api/quests', methods=['GET'])
def get_quests():
    quests = get_quests_model()

    return jsonify({
        "success": True,
        "quests": quests
    })


# Daily Quest sil
@tasks_bp.route('/api/quests/<int:quest_id>', methods=['DELETE'])
def delete_quest(quest_id):
    deleted = delete_quest_model(quest_id)

    if not deleted:
        return jsonify({
            "success": False,
            "error": "Quest not found."
        }), 404

    return jsonify({
        "success": True
    })


# Görevler sayfası
@tasks_bp.route('/tasks')
def tasks_page():
    return render_template("tasks.html", categories=get_catalog())


# Görev kataloğunu getir
@tasks_bp.route('/api/tasks')
def task_catalog():
    return jsonify({
        "categories": get_catalog(),
        "task_count": sum(
            len(category["tasks"])
            for category in get_catalog()
        )
    })


# Görev öner
@tasks_bp.route('/api/tasks/recommend', methods=['POST'])
def recommend_task():
    payload = request.get_json(silent=True) or {}

    need = payload.get("need")
    context = TaskRecommendationContext.for_need(need)

    if context is None:
        return jsonify({
            "success": False,
            "error": "Choose a valid focus state."
        }), 400

    try:
        max_duration = max(
            1,
            min(5, int(payload.get("max_duration", 3)))
        )
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Choose a valid break duration."
        }), 400

    exclude_ids = payload.get("exclude_ids", [])

    if not isinstance(exclude_ids, list):
        exclude_ids = []

    task = context.recommend(
        max_duration=max_duration,
        exclude_ids=exclude_ids
    )

    if task is None:
        return jsonify({
            "success": False,
            "error": "No task in this category fits that time. Choose a longer break."
        }), 422

    category_name = next(
        category["name"]
        for category in CATEGORIES
        if category["id"] == task["category"]
    )

    return jsonify({
        "success": True,
        "task": task,
        "category_name": category_name
    })


# Görevi tamamla
@tasks_bp.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    payload = request.get_json(silent=True) or {}

    task = get_task(payload.get("task_id"))

    if task is None:
        return jsonify({
            "success": False,
            "error": "Task not found."
        }), 404

    result, status_code = complete_task_model(task)

    return jsonify(result), status_code
