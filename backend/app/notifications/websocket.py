import json

from backend.app.utils.helpers import logger

# Import the global dict from main
from backend.app.main import connected_websockets


async def broadcast_notification(user_id: str, notification: dict):
    """Send a real-time notification to the user's WebSocket connections."""
    if user_id not in connected_websockets:
        return
    message = json.dumps(notification, default=str)
    stale = []
    for ws in connected_websockets[user_id]:
        try:
            await ws.send_text(message)
        except Exception:
            stale.append(ws)
    for ws in stale:
        try:
            connected_websockets[user_id].remove(ws)
        except ValueError:
            pass
    logger.debug(f"Broadcasted notification to user {user_id}")
