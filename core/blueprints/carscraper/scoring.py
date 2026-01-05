# CarScraper Scoring Module
# Z-Score kalkulácia a AI analýza

import json
from typing import Dict, List, Optional
from statistics import mean, stdev
from core.extensions import logger


def calculate_z_score(value: float, values: List[float]) -> float:
    """
    Vypočíta Z-Score pre hodnotu vzhľadom k zoznamu hodnôt
    Z-Score = (value - mean) / std
    """
    if len(values) < 2:
        return 0.0
    
    try:
        m = mean(values)
        s = stdev(values)
        if s == 0:
            return 0.0
        return (value - m) / s
    except Exception:
        return 0.0


def calculate_deal_score(
    price: float,
    km: int,
    year: int,
    all_prices: List[float],
    all_kms: List[int],
    price_weight: float = 0.6,
    km_weight: float = 0.3,
    year_weight: float = 0.1
) -> Dict:
    """
    Vypočíta skóre pre deal
    
    Váhy:
    - Cena: 60% (nižšia = lepšie, preto negujeme)
    - Kilometre: 30% (nižšie = lepšie, preto negujeme)
    - Rok: 10% (novší = lepšie)
    
    Returns:
        Dict s score, verdict, a detailami
    """
    current_year = 2024
    
    # Z-Scores (negované pre cenu a km, lebo nižšie = lepšie)
    z_price = -calculate_z_score(price, all_prices) if all_prices else 0.0
    z_km = -calculate_z_score(km, [float(k) for k in all_kms]) if all_kms else 0.0
    
    # Year bonus (0-10 rokov = 0-1.0)
    age = current_year - year if year else 5
    year_bonus = max(0, min(1, (10 - age) / 10))
    
    # Vážený priemer
    score = (z_price * price_weight) + (z_km * km_weight) + (year_bonus * year_weight)
    
    # Verdict podľa score
    if score > 1.5:
        verdict = 'SUPER_DEAL'
        risk_level = 'Nízke'
    elif score > 0.5:
        verdict = 'GOOD_DEAL'
        risk_level = 'Nízke'
    elif score > -0.5:
        verdict = 'OK'
        risk_level = 'Stredné'
    else:
        verdict = 'SKIP'
        risk_level = 'Vysoké'
    
    return {
        'score': round(score, 2),
        'verdict': verdict,
        'risk_level': risk_level,
        'details': {
            'z_price': round(z_price, 2),
            'z_km': round(z_km, 2),
            'year_bonus': round(year_bonus, 2)
        }
    }


def score_deals(deals: List[Dict]) -> List[Dict]:
    """
    Aplikuje scoring na zoznam deals
    
    Args:
        deals: Zoznam deals s price, km, year
    
    Returns:
        Zoznam deals s pridaným score, verdict, risk_level
    """
    if not deals:
        return deals
    
    # Extrahuj hodnoty pre štatistiku
    prices = [d.get('price', 0) for d in deals if d.get('price')]
    kms = [d.get('km', 0) for d in deals if d.get('km')]
    
    # Skóruj každý deal
    for deal in deals:
        price = deal.get('price', 0)
        km = deal.get('km', 0)
        year = deal.get('year', 2020)
        
        result = calculate_deal_score(
            price=price,
            km=km,
            year=year,
            all_prices=prices,
            all_kms=kms
        )
        
        deal['score'] = result['score']
        deal['verdict'] = result['verdict']
        deal['risk_level'] = result['risk_level']
    
    # Zoraď podľa score (najlepšie prvé)
    deals.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return deals


def get_ai_analysis(deal: Dict, openai_client=None) -> Optional[Dict]:
    """
    Získa AI analýzu pre deal (volá sa len pre SUPER_DEAL)
    
    Args:
        deal: Dict s informáciami o aute
        openai_client: OpenAI client (optional, inak sa použije z konfigurácie)
    
    Returns:
        Dict s AI analýzou alebo None
    """
    if not openai_client:
        try:
            import httpx
            from openai import OpenAI
            from flask import current_app
            
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OpenAI API key nie je nakonfigurovaný")
                return None
            
            http_client = httpx.Client(trust_env=False)
            openai_client = OpenAI(api_key=api_key, http_client=http_client)
        except Exception as e:
            logger.error(f"Chyba pri inicializácii OpenAI: {e}")
            return None
    
    prompt = f"""
Analyzuj tento inzerát na auto a identifikuj potenciálne riziká:

Značka/Model: {deal.get('title', 'Neznáme')}
Cena: {deal.get('price', 0)} EUR
Kilometre: {deal.get('km', 0)} km
Rok výroby: {deal.get('year', 'Neznámy')}
Lokalita: {deal.get('location', 'Neznáma')}
Popis: {deal.get('description', 'Bez popisu')[:500]}

Odpovedz VÝHRADNE v JSON formáte (žiadny markdown):
{{
  "risks": ["riziko1", "riziko2"],
  "red_flags": ["varovanie1"],
  "recommendation": "KÚPIŤ/OVERIŤ/NEKUPOVAŤ",
  "estimated_market_value": 12000,
  "summary": "Stručné zhrnutie v 1-2 vetách"
}}
"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Si expert na jazdené autá. Odpovedaj výhradne v JSON formáte."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON
        try:
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            # Skús extrahovať JSON z odpovede
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {'summary': content}
    
    except Exception as e:
        logger.error(f"AI analýza zlyhala: {e}")
        return None
