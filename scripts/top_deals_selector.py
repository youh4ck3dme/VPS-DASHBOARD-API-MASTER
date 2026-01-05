#!/usr/bin/env python3
"""
TOP Deals Selector - AI výber 6 najziskovejších ponúk dňa
Spúšťať cez cron o 00:05 každý deň
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models.car_deal import CarDeal


def select_top_deals():
    """
    Vyberá 6 najziskovejších ponúk z posledných 24 hodín.
    Kritériá:
    - Najvyššie skóre (score)
    - Najnižší risk level
    - Verdikt = KÚPIŤ
    """
    with app.app_context():
        today = date.today()
        
        # Resetuj staré top deals
        CarDeal.query.filter(
            CarDeal.is_top_deal == True,
            CarDeal.top_deal_date < today
        ).update({'is_top_deal': False, 'top_deal_date': None})
        
        # Vyber nové TOP 6
        top_deals = CarDeal.query.filter(
            CarDeal.verdict == 'KÚPIŤ',
            CarDeal.score.isnot(None)
        ).order_by(
            CarDeal.score.desc(),
            CarDeal.risk_level.asc()
        ).limit(6).all()
        
        count = 0
        for deal in top_deals:
            deal.is_top_deal = True
            deal.top_deal_date = today
            count += 1
            print(f"🏆 TOP Deal #{count}: {deal.title} (score: {deal.score})")
        
        db.session.commit()
        print(f"\n✅ Vybraných {count} TOP ponúk pre {today}")
        return count


if __name__ == '__main__':
    print("🎯 TOP Deals Selector - Spúšťam výber...")
    select_top_deals()
