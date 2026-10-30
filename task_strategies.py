"""Strategy Pattern implementation for focus-reset task recommendations."""

import random
from abc import ABC, abstractmethod

from task_library import TASKS


class TaskRecommendationStrategy(ABC):
    category_id = None

    @abstractmethod
    def recommend(self, max_duration=5, exclude_ids=None):
        """Pick a task from this strategy's own category."""


class CategoryStrategy(TaskRecommendationStrategy):
    def __init__(self, category_id):
        self.category_id = category_id

    def recommend(self, max_duration=5, exclude_ids=None):
        exclude_ids = set(exclude_ids or [])
        category_tasks = [task for task in TASKS if task["category"] == self.category_id]
        duration_matches = [task for task in category_tasks if task["duration"] <= max_duration]
        candidates = duration_matches
        if not candidates:
            return None
        fresh_candidates = [task for task in candidates if task["id"] not in exclude_ids]
        return random.choice(fresh_candidates or candidates)


class PhysicalResetStrategy(CategoryStrategy):
    def __init__(self):
        super().__init__("physical_reset")


class MindfulnessStrategy(CategoryStrategy):
    def __init__(self):
        super().__init__("mindfulness_relaxation")


class SensoryResetStrategy(CategoryStrategy):
    def __init__(self):
        super().__init__("sensory_reset")


class CreativeBreakStrategy(CategoryStrategy):
    def __init__(self):
        super().__init__("creative_breaks")


class CognitiveGameStrategy(CategoryStrategy):
    def __init__(self):
        super().__init__("cognitive_mini_games")


class TaskRecommendationContext:
    """Select and execute the strategy that matches the selected focus state."""

    STRATEGIES = {
        "mentally_tired": MindfulnessStrategy,
        "anxious": MindfulnessStrategy,
        "distracted": SensoryResetStrategy,
        "need_movement": PhysicalResetStrategy,
        "creative_break": CreativeBreakStrategy,
        "brain_game": CognitiveGameStrategy,
    }

    def __init__(self, strategy):
        self.strategy = strategy

    @classmethod
    def for_need(cls, need):
        strategy_type = cls.STRATEGIES.get(need)
        if strategy_type is None:
            return None
        return cls(strategy_type())

    def recommend(self, max_duration=5, exclude_ids=None):
        return self.strategy.recommend(max_duration=max_duration, exclude_ids=exclude_ids)
