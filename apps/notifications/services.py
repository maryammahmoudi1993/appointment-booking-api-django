import datetime
import hashlib
import hmac
import json
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def _create_notification_record(
    business=None,
    recipient=None,
    recipient_email="",
    notification_type="email",
    subject="",
    body="",
):
    from .models import Notification

    return Notification.objects.create(
        business=business,
        recipient=recipient,
        recipient_email=recipient_email or (recipient.email if recipient else ""),
        notification_type=notification_type,
        subject=subject,
        body=body,
    )


def deliver_webhook(subscription, event_type, payload):
    import requests

    body = json.dumps(payload, default=_json_serial, ensure_ascii=False).encode("utf-8")
    signature = _sign_body(body, subscription.secret) if subscription.secret else ""

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Event": event_type,
        "User-Agent": "BloomFlow-Webhook/1.0",
    }

    from .models import WebhookDelivery

    delivery = WebhookDelivery.objects.create(
        subscription=subscription,
        event_type=event_type,
        payload=payload,
    )

    try:
        resp = requests.post(subscription.url, data=body, headers=headers, timeout=10)
        delivery.response_status = resp.status_code
        delivery.response_body = resp.text[:2000]
        if 200 <= resp.status_code < 300:
            delivery.status = "success"
            delivery.completed_at = timezone.now()
            logger.info(
                "Webhook %s delivered to %s (HTTP %d)",
                delivery.id,
                subscription.url,
                resp.status_code,
            )
        else:
            delivery.status = "failed"
            delivery.error_message = f"HTTP {resp.status_code}: {resp.text[:200]}"
            logger.warning(
                "Webhook %s failed at %s (HTTP %d)",
                delivery.id,
                subscription.url,
                resp.status_code,
            )
    except requests.RequestException as exc:
        delivery.status = "failed"
        delivery.error_message = str(exc)[:500]
        logger.error("Webhook %s error for %s: %s", delivery.id, subscription.url, exc)

    delivery.save(
        update_fields=[
            "status",
            "response_status",
            "response_body",
            "error_message",
            "completed_at",
        ]
    )
    return delivery


def _sign_body(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def _json_serial(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
