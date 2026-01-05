# CarScraper Telegram Notifications
# Notifikácie pre SUPER_DEAL a denný digest

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Telegram bot import
try:
    import telegram
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot nie je nainštalovaný. pip install python-telegram-bot")


class TelegramNotifier:
    """
    Telegram notifikácie pre CarScraper Pro
    
    Konfigurácia v .env:
        TELEGRAM_BOT_TOKEN=xxx
        TELEGRAM_ADMIN_CHAT_ID=xxx
    """
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        self.bot = None
        
        if TELEGRAM_AVAILABLE and self.bot_token:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot inicializovaný")
            except Exception as e:
                logger.error(f"Chyba pri inicializácii Telegram bota: {e}")
    
    def is_available(self) -> bool:
        """Skontroluje či je Telegram dostupný"""
        return self.bot is not None
    
    def format_deal_message(self, deal: Dict) -> str:
        """Formátuje deal pre Telegram správu"""
        verdict_emoji = {
            'SUPER_DEAL': '🔥',
            'GOOD_DEAL': '👍',
            'OK': '➡️',
            'SKIP': '⛔'
        }
        
        emoji = verdict_emoji.get(deal.get('verdict', ''), '🚗')
        
        message = f"""
{emoji} *{deal.get('verdict', 'DEAL')}*

*{deal.get('title', 'Bez názvu')}*

💰 *Cena:* {deal.get('price', 0):,.0f} €
{f"📊 *Trhová hodnota:* {deal.get('market_value', 0):,.0f} €" if deal.get('market_value') else ""}
{f"💵 *Potenciálny zisk:* {deal.get('profit', 0):,.0f} €" if deal.get('profit') else ""}
📍 *Lokalita:* {deal.get('location', 'Neznáma')}
🚗 *Kilometre:* {deal.get('km', 0):,} km
📅 *Rok:* {deal.get('year', 'N/A')}
⭐ *Skóre:* {deal.get('score', 0):.2f}

🔗 [Otvoriť inzerát]({deal.get('link', '#')})
"""
        return message.strip()
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = 'Markdown') -> bool:
        """Pošle správu do Telegram chatu"""
        if not self.bot:
            logger.warning("Telegram bot nie je dostupný")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            logger.info(f"Telegram správa odoslaná do {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Chyba pri odosielaní Telegram správy: {e}")
            return False
    
    async def notify_super_deal(self, deal: Dict, chat_id: str) -> bool:
        """Pošle notifikáciu o SUPER_DEAL"""
        message = self.format_deal_message(deal)
        return await self.send_message(chat_id, message)
    
    async def send_daily_digest(self, deals: List[Dict], chat_id: str) -> bool:
        """Pošle denný prehľad top deals"""
        if not deals:
            return False
        
        header = f"""
📊 *DENNÝ PREHĽAD CARSCRAPERU*
_{datetime.now().strftime('%d.%m.%Y')}_

Nájdených *{len(deals)}* najlepších ponúk:
"""
        
        messages = [header]
        for i, deal in enumerate(deals[:5], 1):
            messages.append(f"""
*{i}. {deal.get('title', 'N/A')}*
   💰 {deal.get('price', 0):,.0f} € | ⭐ {deal.get('score', 0):.2f}
   🔗 [Otvoriť]({deal.get('link', '#')})
""")
        
        full_message = '\n'.join(messages)
        return await self.send_message(chat_id, full_message)


# Sync wrapper pre použitie bez async
def send_deal_notification(deal: Dict, chat_id: str, bot_token: Optional[str] = None) -> bool:
    """
    Synchronný wrapper pre poslanie notifikácie o deale
    
    Použitie:
        from app.blueprints.carscraper.notifications import send_deal_notification
        send_deal_notification(deal_dict, 'CHAT_ID')
    """
    import asyncio
    
    notifier = TelegramNotifier(bot_token)
    if not notifier.is_available():
        return False
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(notifier.notify_super_deal(deal, chat_id))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Chyba pri sync notifikácii: {e}")
        return False


def send_digest(deals: List[Dict], chat_id: str, bot_token: Optional[str] = None) -> bool:
    """Synchronný wrapper pre denný digest"""
    import asyncio
    
    notifier = TelegramNotifier(bot_token)
    if not notifier.is_available():
        return False
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(notifier.send_daily_digest(deals, chat_id))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Chyba pri digest notifikácii: {e}")
        return False
