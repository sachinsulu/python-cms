import re

def normalize_phone(value):
    """
    Cleans a phone number by removing internal spaces and prepending +977 if missing.
    """
    if not value:
        return ""
    
    # 1. Strip whitespace
    p = str(value).strip()
    if not p:
        return ""
        
    # 2. Remove all spaces, dashes, parentheses
    p_clean = re.sub(r'[\s\-()]+', '', p)
    
    # 3. Add +977 if missing
    if not p_clean.startswith('+'):
        # If the number starts with 977, treat it as the country code
        if p_clean.startswith('977'):
            p_clean = '+' + p_clean
        else:
            # If it's a typical mobile (98X) or landline (01X)
            # Remove leading 0 if it exists before adding +977? 
            # Nepal's country code is +977. Landlines are +977 1XXXXXXX. 
            # If user provides 01XXXXXXX, we can keep the 0 or remove it. Both work usually.
            p_clean = '+977' + p_clean
            
    # 4. Format for display: "+977 98XXXXXXXX"
    if p_clean.startswith('+977'):
        # Ensure we don't have multiple +977 prefixes if they were already there
        # This handles cases like +97+977 (unlikely but possible during messy edits)
        p_clean = '+' + re.sub(r'^(\+)+', '', p_clean)
        if p_clean.startswith('+977'):
             return '+977 ' + p_clean[4:]
    return p_clean

def split_and_normalize_phones(value):
    """
    Splits by delimiters and normalizes each number.
    """
    if not value:
        return []
    import re
    # Split by comma, pipe, or semicolon
    parts = re.split(r'[|;,]', str(value))
    normalized = []
    for p in parts:
        formatted = normalize_phone(p)
        if formatted:
            normalized.append(formatted)
    return normalized
