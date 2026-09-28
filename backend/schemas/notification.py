"""
schemas/notification.py — Pydantic schemas for notification API endpoints.
"""
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Single notification as returned by GET /notifications."""
    notification_id: str
    policyholder_id: str
    policy_id: str
    payout_id: str
    event_type: str
    title: str
    message: str
    status: str
    created_at: datetime
    acknowledged_at: datetime | None = None
    metadata: dict | None = None


class NotificationListResponse(BaseModel):
    """Response for GET /notifications."""
    notifications: list[NotificationResponse]
    total: int


class AcknowledgeResponse(BaseModel):
    """Response for POST /notifications/{id}/acknowledge."""
    notification_id: str
    status: str
    acknowledged_at: datetime
