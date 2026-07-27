from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.repositories import payment_link_repo
from app.schemas.payment_link import PaymentLinkCreate

def format_payment_link(link: dict) -> dict:
    if link:
        # Build the pay_url
        link["pay_url"] = f"/pay/{link['id']}"
    return link

def create_payment_link(merchant_id: str, link_in: PaymentLinkCreate) -> dict:
    if link_in.expires_in_minutes:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=link_in.expires_in_minutes)
    else:
        # Default expiry 24h
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    link = payment_link_repo.create_payment_link(
        merchant_id=merchant_id,
        amount=float(link_in.amount),
        currency=link_in.currency,
        description=link_in.description,
        expires_at=expires_at,
        status="created"
    )
    return format_payment_link(link)

import logging
from app.db import cache

logger = logging.getLogger(__name__)

def get_payment_link(link_id: str) -> Optional[dict]:
    cache_key = f"payment_link:{link_id}"
    link = cache.get_json(cache_key)
    
    if link:
        logger.info(f"Cache hit for payment_link:{link_id}")
        if link.get("expires_at") and isinstance(link["expires_at"], str):
            link["expires_at"] = datetime.fromisoformat(link["expires_at"])
        if link.get("created_at") and isinstance(link["created_at"], str):
            link["created_at"] = datetime.fromisoformat(link["created_at"])
    else:
        link = payment_link_repo.get_payment_link_by_id(link_id)
        if not link:
            return None
        cache.set_json(cache_key, link, ttl_seconds=60)
    
    # Check expiry
    if link["status"] == "created" and link["expires_at"]:
        # If DB returned naive datetime but we compare with aware, we handle it if it worked before.
        # Let's ensure we can compare them
        if link["expires_at"].tzinfo is None:
            link["expires_at"] = link["expires_at"].replace(tzinfo=timezone.utc)
            """
            Python does not allow comparing these:

            naive > aware

            You'll get

            TypeError:
            can't compare offset-naive and offset-aware datetimes

            So they fix it.

            link["expires_at"] = link["expires_at"].replace(
                tzinfo=timezone.utc
            )

            This makes it timezone-aware.
            """
        if datetime.now(timezone.utc) > link["expires_at"]:
            # Flip to expired
            link = payment_link_repo.update_payment_link_status(link_id, "expired")
            cache.delete(cache_key)
            
    return format_payment_link(link)

def list_merchant_payment_links(merchant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    links = payment_link_repo.list_payment_links_by_merchant(merchant_id, limit, offset)
    return [format_payment_link(link) for link in links]
