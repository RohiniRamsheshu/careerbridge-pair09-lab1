"""User confirmation for assistant actions.

Pending actions are deliberately kept out of the database: they are short-lived,
single-use capabilities tied to a user and the exact item proposed.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from threading import Lock


@dataclass
class PendingAction:
    action_id: str
    user_id: int
    tool_name: str
    arguments: dict
    expires_at: datetime
    used: bool = False


_ACTIONS: dict[str, PendingAction] = {}
_LOCK = Lock()
ACTION_TTL = timedelta(minutes=10)


def confirm_action(tool_name, arguments, auto_approve=False, user_id=None):
    """Create a pending action, or explicitly approve an action.

    ``auto_approve`` is intentionally rejected for external callers.  The
    approval endpoint consumes the returned action id through ``approve_action``.
    """
    if tool_name != "save_job_or_event":
        return {"confirmed": True}
    if auto_approve:
        return {"confirmed": False, "error": "automatic approval is disabled"}
    if not isinstance(user_id, int) or not isinstance(arguments, dict):
        return {"confirmed": False, "error": "invalid confirmation context"}
    action_id = token_urlsafe(24)
    action = PendingAction(
        action_id=action_id,
        user_id=user_id,
        tool_name=tool_name,
        arguments=dict(arguments),
        expires_at=datetime.now(timezone.utc) + ACTION_TTL,
    )
    with _LOCK:
        _ACTIONS[action_id] = action
    return {
        "confirmed": False,
        "pending": True,
        "action_id": action_id,
        "tool_name": tool_name,
        "arguments": dict(arguments),
        "expires_at": action.expires_at.isoformat(),
    }


def approve_action(action_id, user_id, approved):
    """Consume one exact pending action for its owning student."""
    with _LOCK:
        action = _ACTIONS.get(action_id)
        if not action:
            return None, "unknown confirmation action"
        if action.user_id != user_id:
            return None, "confirmation action belongs to another student"
        if action.used:
            return None, "confirmation action was already used"
        if datetime.now(timezone.utc) >= action.expires_at:
            action.used = True
            return None, "confirmation action expired"
        action.used = True
        if not approved:
            return action, "cancelled"
        return action, None


def clear_actions():
    with _LOCK:
        _ACTIONS.clear()
