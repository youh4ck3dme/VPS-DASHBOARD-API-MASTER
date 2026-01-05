import re

BRANDS = {
    'skoda': ['octavia', 'fabia', 'superb', 'kodiaq', 'karoq', 'scala', 'kamiq', 'rapid', 'yeti', 'citigo', 'felicia'],
    'volkswagen': ['golf', 'passat', 'tiguan', 'touareg', 'polo', 'touran', 'arteon', 'up', 'transporter', 'multivan', 'sharan', 'caddy'],
    'vw': ['golf', 'passat', 'tiguan', 'touareg', 'polo', 'touran', 'arteon', 'up', 'transporter', 'multivan', 'sharan', 'caddy'],
    'bmw': ['320', '330', '520', '530', 'x5', 'x3', 'x1', '1', '7', 'x6', '4', 'x7', 'i3', 'i8', 'z4'],
    'audi': ['a3', 'a4', 'a6', 'q7', 'q5', 'q3', 'a5', 'a8', 'q8', 'tt', 'a7'],
    'mercedes': ['c', 'e', 's', 'a', 'b', 'gle', 'glc', 'gla', 'cls', 'g', 'v'],
    'mercedes-benz': ['c', 'e', 's', 'a', 'b', 'gle', 'glc', 'gla', 'cls', 'g', 'v'],
    'ford': ['focus', 'mondeo', 'fiesta', 'kuga', 's-max', 'c-max', 'ranger', 'mustang'],
    'toyota': ['corolla', 'yaris', 'rav4', 'camry', 'c-hr', 'auris', 'avensis', 'land cruiser', 'hilux'],
    'hyundai': ['i30', 'tucson', 'santa fe', 'i20', 'i40', 'kona', 'ioniq'],
    'kia': ['ceed', 'sportage', 'sorento', 'rio', 'stonic'],
    'renault': ['clio', 'megane', 'captur', 'kadjar', 'scenic', 'talisman', 'zoe'],
    'peugeot': ['208', '308', '2008', '3008', '5008', '508'],
    'opel': ['astra', 'corsa', 'insignia', 'mokka', 'grandland', 'crossland'],
    'dacia': ['duster', 'sandero', 'logan', 'jogger', 'lodgy'],
    'fiat': ['500', 'tipo', 'panda', 'ducato', 'punto'],
    'seat': ['leon', 'ibiza', 'ateca', 'arona', 'tarraco', 'alhambra'],
}

REGIONS_MAPPING = {
    'bratislav': 'Bratislavský',
    'trnav': 'Trnavský',
    'trenc': 'Trenčiansky',
    'nitr': 'Nitriansky',
    'zilin': 'Žilinský',
    'bansk': 'Banskobystrický',
    'presov': 'Prešovský',
    'kosic': 'Košický',
    'senec': 'Bratislavský',
    'pezinok': 'Bratislavský',
    'malacky': 'Bratislavský',
    'galanta': 'Trnavský',
    'dunajska': 'Trnavský',
    'piestany': 'Trnavský',
    'poprad': 'Prešovský',
    'martin': 'Žilinský',
    'michalovce': 'Košický',
    'zvolen': 'Banskobystrický',
}

def parse_car_title(title):
    """
    Parsuje značku a model z nadpisu inzerátu.
    Napr. "Škoda Octavia Combi 2.0 TDI" -> ("Skoda", "Octavia")
    """
    if not title:
        return None, None
        
    title_lower = title.lower()
    found_brand = None
    found_model = None
    
    # Hľadaj značku
    for brand, models in BRANDS.items():
        if brand in title_lower:
            found_brand = 'Volkswagen' if brand == 'vw' else brand.capitalize()
            # Hľadaj model
            for model in models:
                if model in title_lower:
                    found_model = model.capitalize()
                    break
            break
            
    if not found_brand:
        # Hľadaj aspoň v prvom slove ak to vyzerá ako značka
        parts = title.split()
        if parts:
            potential_brand = parts[0].lower()
            if len(potential_brand) > 2:
                found_brand = parts[0].capitalize()

    return found_brand, found_model

def parse_region(location_text):
    """
    Normalizuje lokalitu na kraj.
    Napr. "Bratislava - Staré mesto" -> "Bratislavský"
    """
    if not location_text:
        return None
        
    loc_lower = location_text.lower()
    
    # Priame mapovanie krajov
    for key, value in REGIONS_MAPPING.items():
        if key in loc_lower:
            return value
            
    return location_text  # Vráť pôvodný text ak nevieme priradiť

def is_blacklisted(text):
    """
    Kontroluje, či text obsahuje nepovolených predajcov (Blacklist).
    Aktuálne: AAA Auto
    """
    if not text:
        return False
    
    blacklist = ["aaa auto", "aaaauto", "automoto aaa"]
    text_lower = str(text).lower()
    
    for item in blacklist:
        if item in text_lower:
            return True
            
    return False
