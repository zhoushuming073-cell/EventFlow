"""创建 Space 时按模板预置的卡片。"""

from app.models.card import TYPE_DURATION, TYPE_POINT

TEMPLATE_CARDS: dict[str, list[dict]] = {
    "baby": [
        {"name": "喝奶", "icon": "🍼", "type": TYPE_POINT},
        {"name": "睡觉", "icon": "😴", "type": TYPE_DURATION},
        {"name": "换尿布", "icon": "💩", "type": TYPE_POINT},
        {"name": "辅食", "icon": "🥣", "type": TYPE_POINT},
        {"name": "洗澡", "icon": "🛁", "type": TYPE_DURATION},
    ],
    "study": [
        {"name": "自习", "icon": "📚", "type": TYPE_DURATION},
        {"name": "上课", "icon": "🏫", "type": TYPE_DURATION},
        {"name": "编程", "icon": "💻", "type": TYPE_DURATION},
        {"name": "运动", "icon": "🏃", "type": TYPE_DURATION},
        {"name": "游戏", "icon": "🎮", "type": TYPE_DURATION},
    ],
    "daily": [
        {"name": "起床", "icon": "⏰", "type": TYPE_POINT},
        {"name": "睡觉", "icon": "😴", "type": TYPE_DURATION},
        {"name": "吃饭", "icon": "🍚", "type": TYPE_POINT},
        {"name": "工作", "icon": "💼", "type": TYPE_DURATION},
        {"name": "通勤", "icon": "🚇", "type": TYPE_DURATION},
        {"name": "锻炼", "icon": "🏃", "type": TYPE_DURATION},
    ],
    "pet": [
        {"name": "喂食", "icon": "🍖", "type": TYPE_POINT},
        {"name": "遛弯", "icon": "🦮", "type": TYPE_DURATION},
        {"name": "喝水", "icon": "💧", "type": TYPE_POINT},
        {"name": "便便", "icon": "💩", "type": TYPE_POINT},
        {"name": "玩耍", "icon": "🎾", "type": TYPE_DURATION},
        {"name": "睡觉", "icon": "😴", "type": TYPE_DURATION},
    ],
}
