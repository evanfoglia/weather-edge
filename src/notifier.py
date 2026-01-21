"""
Notification system for weather arbitrage alerts.

Logs prominently when opportunities are detected.
Optional webhook support for mobile push notifications.
"""
import asyncio
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)


class AlertNotifier:
    """Logs alerts when arbitrage opportunities are detected."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("ALERT_WEBHOOK_URL")
        self.last_alert_time = 0
        self.cooldown_seconds = 60  # Don't spam alerts
        
    def _can_alert(self) -> bool:
        """Check if we're past the cooldown period."""
        now = time.time()
        if now - self.last_alert_time > self.cooldown_seconds:
            self.last_alert_time = now
            return True
        return False
    
    async def send_webhook(self, title: str, message: str):
        """Send alert via webhook (ntfy.sh, Pushover, etc.)."""
        if not self.webhook_url:
            return
            
        try:
            import aiohttp
            import ssl
            import certifi
            
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Supports ntfy.sh format
                if "ntfy.sh" in self.webhook_url:
                    await session.post(
                        self.webhook_url,
                        data=message.encode('utf-8'),
                        headers={"Title": title, "Priority": "high"}
                    )
                else:
                    # Generic JSON webhook
                    await session.post(
                        self.webhook_url,
                        json={"title": title, "message": message}
                    )
                logger.info(f"Webhook alert sent")
        except Exception as e:
            logger.warning(f"Failed to send webhook: {e}")
    
    async def alert(self, title: str, message: str, force: bool = False):
        """
        Log an alert prominently.
        
        Args:
            title: Alert title
            message: Alert body
            force: Bypass cooldown if True
        """
        if not force and not self._can_alert():
            logger.debug("Alert suppressed (cooldown)")
            return
        
        # Just log prominently
        logger.info("")
        logger.info("🔔" + "=" * 50)
        logger.info(f"🔔 ALERT: {title}")
        logger.info(f"🔔 {message}")
        logger.info("🔔" + "=" * 50)
        logger.info("")
        
        if self.webhook_url:
            await self.send_webhook(title, message)
    
    async def opportunity_alert(self, city: str, ticker: str, edge: float, action: str):
        """Log a formatted opportunity alert."""
        title = f"Weather Arb: {city.upper()}"
        message = f"{action} {ticker} | Edge: {edge*100:.1f}%"
        await self.alert(title, message)
