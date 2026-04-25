import logging
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.message import Message
from app.services.match_notify_service import MatchNotifyService

log = logging.getLogger(__name__)


def run_weekly_item_maintenance(db: Session) -> dict:
    """每周提醒一次，并在到期后自动关闭。"""
    now = datetime.now()
    week_tag = now.strftime("%Y-%W")
    remind_count = 0
    close_count = 0

    active_items = (
        db.query(Item)
        .filter(Item.is_deleted == 0, Item.status == 1)
        .all()
    )

    for item in active_items:
        status_text = "寻物是否已找回" if item.item_type == 1 else "招领是否已认领"
        remind_msg = f"[系统提醒周报 {week_tag}] 请确认“{item.title}”的状态：{status_text}"

        exists = (
            db.query(Message.id)
            .filter(
                Message.item_id == item.id,
                Message.to_user_id == item.user_id,
                Message.content == remind_msg,
            )
            .first()
        )
        if not exists:
            db.add(
                Message(
                    from_user_id=item.user_id,
                    to_user_id=item.user_id,
                    item_id=item.id,
                    content=remind_msg,
                    is_read=0,
                )
            )
            remind_count += 1

        if item.expires_at and item.expires_at < now:
            item.status = 3
            item.closed_at = now
            close_count += 1

    db.commit()
    result = {"weekly_remind_count": remind_count, "auto_close_count": close_count}
    log.info("weekly maintenance finished: %s", result)
    return result


def run_daily_match_scan(db: Session) -> dict:
    """
    每日重扫“未关闭寻物帖”，命中>=90%则写入站内匹配通知。
    使用已有去重逻辑，避免重复推送同一目标帖。
    """
    now = datetime.now()
    open_lost_items = (
        db.query(Item.id)
        .filter(
            Item.item_type == 1,
            Item.status == 1,
            Item.is_deleted == 0,
            or_(Item.expires_at == None, Item.expires_at >= now),  # noqa: E711
        )
        .all()
    )

    notify_service = MatchNotifyService(db)
    created = 0
    scanned = 0
    for row in open_lost_items:
        scanned += 1
        try:
            created += notify_service.notify_for_new_item(row.id)
        except Exception as exc:
            log.warning("daily match scan failed for item_id=%s: %s", row.id, exc)

    result = {"scanned_items": scanned, "created_match_messages": created}
    log.info("daily match scan finished: %s", result)
    return result
