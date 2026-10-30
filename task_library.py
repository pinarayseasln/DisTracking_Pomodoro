"""Task catalog for the Tasks area and focus reset recommendations."""

from copy import deepcopy


CATEGORIES = [
    {"id": "physical_reset", "name": "Physical Reset", "description": "Short movement breaks to release physical tension."},
    {"id": "mindfulness_relaxation", "name": "Mindfulness & Relaxation", "description": "Breathing and reflection breaks to slow down."},
    {"id": "sensory_reset", "name": "Sensory Reset", "description": "Reconnect with your surroundings through your senses."},
    {"id": "creative_breaks", "name": "Creative Breaks", "description": "Low-pressure creative activities away from study work."},
    {"id": "cognitive_mini_games", "name": "Cognitive Mini-Games", "description": "Tiny attention, memory and puzzle challenges."},
]


TASKS = [
    {"id": "PR01", "title": "Stand up and stretch", "category": "physical_reset", "duration": 2, "xp": 10, "description": "Stand up, reach your arms overhead, then gently stretch your shoulders and sides."},
    {"id": "PR02", "title": "Take a short walk", "category": "physical_reset", "duration": 5, "xp": 20, "description": "Walk around your home or hallway at an easy pace and let your eyes leave the screen."},
    {"id": "PR03", "title": "Wrist and finger break", "category": "physical_reset", "duration": 1, "xp": 10, "description": "Open and close your hands, circle your wrists gently, and stretch your fingers."},
    {"id": "PR04", "title": "Mini movement break", "category": "physical_reset", "duration": 2, "xp": 15, "description": "Do 10 heel raises, 10 relaxed shoulder rolls, then march gently in place."},
    {"id": "PR05", "title": "Look into the distance", "category": "physical_reset", "duration": 2, "xp": 10, "description": "Look away from your screen at a distant object and let your eyes rest without straining."},

    {"id": "MR01", "title": "Controlled breathing", "category": "mindfulness_relaxation", "duration": 3, "xp": 20, "description": "Breathe in comfortably for four counts and out for six. Keep the breath easy; return to a natural rhythm if it feels uncomfortable."},
    {"id": "MR02", "title": "Mindfulness pause", "category": "mindfulness_relaxation", "duration": 2, "xp": 15, "description": "Notice your breathing and the sensations around you. When thoughts wander, gently bring your attention back."},
    {"id": "MR03", "title": "Body scan", "category": "mindfulness_relaxation", "duration": 3, "xp": 20, "description": "Move your attention slowly from your feet to your shoulders, noticing sensations without trying to change them."},
    {"id": "MR04", "title": "Clear your mind", "category": "mindfulness_relaxation", "duration": 2, "xp": 15, "description": "Write a few words about what is on your mind. You can leave the note private and return to your work when ready."},

    {"id": "SR01", "title": "Notice nature", "category": "sensory_reset", "duration": 3, "xp": 15, "description": "Look outside or at a plant. Notice a few colors, shapes, and small details you had not seen before."},
    {"id": "SR02", "title": "5-4-3-2-1 senses check", "category": "sensory_reset", "duration": 3, "xp": 20, "description": "Notice five things you see, four you feel, three you hear, two you smell, and one you taste or appreciate."},
    {"id": "SR03", "title": "Drink water mindfully", "category": "sensory_reset", "duration": 1, "xp": 10, "description": "Take a few unhurried sips of water and notice its temperature and taste."},
    {"id": "SR04", "title": "Explore one object", "category": "sensory_reset", "duration": 2, "xp": 15, "description": "Choose a nearby object and notice its color, shape, texture, weight, and small details."},
    {"id": "SR05", "title": "Listen to nature sounds", "category": "sensory_reset", "duration": 3, "xp": 15, "description": "Listen to rain, birds, or another gentle sound. Notice its rhythm and how it changes."},
    {"id": "SR06", "title": "Water break", "category": "sensory_reset", "duration": 1, "xp": 10, "description": "Step away from your desk, get a glass of water, and take a few sips."},

    {"id": "CB01", "title": "Free doodling", "category": "creative_breaks", "duration": 3, "xp": 15, "description": "Draw lines, shapes, or a tiny scene without planning or judging the result."},
    {"id": "CB02", "title": "Daydream break", "category": "creative_breaks", "duration": 2, "xp": 10, "description": "Imagine a place you would enjoy visiting. Picture its colors, sounds, and atmosphere."},
    {"id": "CB03", "title": "Mini coloring break", "category": "creative_breaks", "duration": 3, "xp": 20, "description": "Color a small pattern or sketch using any colors you like. This is a calm placeholder activity for now."},
    {"id": "CB04", "title": "Musical pause", "category": "creative_breaks", "duration": 2, "xp": 15, "description": "Listen to a short piece of music or a calming sound and notice its rhythm and mood."},

    {"id": "CG01", "title": "Visual focus", "category": "cognitive_mini_games", "duration": 1, "xp": 10, "description": "Choose a small object and notice as many visual details as you can for one minute."},
    {"id": "CG02", "title": "Letter hunt", "category": "cognitive_mini_games", "duration": 2, "xp": 15, "description": "Pick a letter and find or list as many words beginning with it as you can in two minutes."},
    {"id": "CG03", "title": "Remember the color sequence", "category": "cognitive_mini_games", "duration": 2, "xp": 15, "description": "Study a short sequence of colors, look away, then try to repeat the sequence from memory."},
    {"id": "CG04", "title": "Spot the difference", "category": "cognitive_mini_games", "duration": 2, "xp": 15, "description": "Compare two similar pictures and find the differences. The interactive puzzle will be added later."},
    {"id": "CG05", "title": "Matching cards", "category": "cognitive_mini_games", "duration": 2, "xp": 15, "description": "Try to find matching pairs by turning over two cards at a time. The game board is a placeholder for now."},
    {"id": "CG06", "title": "Mini Sudoku", "category": "cognitive_mini_games", "duration": 3, "xp": 20, "description": "Try a small 4×4 Sudoku puzzle. The playable puzzle is a placeholder for now."},
    {"id": "CG07", "title": "Remember the sequence", "category": "cognitive_mini_games", "duration": 1, "xp": 10, "description": "Look at a short sequence of symbols, then repeat them in the same order."},
    {"id": "CG08", "title": "Grow your virtual plant", "category": "cognitive_mini_games", "duration": 1, "xp": 10, "description": "Water your virtual plant to help it grow. This is a gamified interaction, not a cognitive exercise."},
]


def get_catalog():
    """Return fresh JSON-ready catalog data."""
    grouped = []
    for category in CATEGORIES:
        grouped.append({
            **category,
            "tasks": [deepcopy(task) for task in TASKS if task["category"] == category["id"]],
        })
    return grouped


def get_task(task_id):
    task = next((item for item in TASKS if item["id"] == task_id), None)
    return deepcopy(task) if task else None
