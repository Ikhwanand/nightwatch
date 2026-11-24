import httpx
from typing import Optional
from nightwatch.config import get_settings


class NotificationService:
    """Dispatches formatted SRE incident notifications and approval requests to Telegram."""

    def __init__(self):
        self.settings = get_settings()

    def send_incident_alert(
        self,
        incident_id: str,
        severity: str,
        cause: str,
        recommended_action: str,
        target_service: str = "sample-app",
    ) -> bool:
        """Formats and dispatches an incident alert to Telegram."""
        severity_emoji = "🚨" if severity in ["P1", "CRITICAL"] else "⚠️"

        message = (
            f"{severity_emoji} *Nightwatch SRE Alert: [{incident_id}]*\n\n"
            f"📌 *Severity:* `{severity}`\n"
            f"🎯 *Target Service:* `{target_service}`\n"
            f"🔍 *Root Cause:* {cause}\n\n"
            f"🛠️ *Recommended Mitigation:*\n`{recommended_action}`\n\n"
            f"⚡ *Action Required:* Awaiting human approval via SRE Mission Control Dashboard:\n"
            f"👉 http://localhost:5173"
        )

        print("\n" + "=" * 50)
        print(f"[NOTIFICATION DISPATCH]\n{message}")
        print("=" * 50 + "\n")

        bot_token = self.settings.telegram_bot_token
        chat_id = self.settings.telegram_chat_id

        if bot_token and chat_id:
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": message,
                            "parse_mode": "Markdown",
                        },
                    )
                    if resp.status_code == 200:
                        print(f"[TELEGRAM] Notification successfully sent for incident {incident_id}")
                        return True
                    else:
                        print(f"[TELEGRAM ERROR] API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"[TELEGRAM ERROR] Telegram dispatch failed: {e}")
        else:
            print("[TELEGRAM] Bot token or chat ID not set. (Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in backend/.env)")

        return True


notification_service = NotificationService()
