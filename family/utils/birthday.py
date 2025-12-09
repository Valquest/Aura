from datetime import date, timedelta

# Average length of a Gregorian year in days
REAL_YEAR_DAYS = 365.2425


def get_family_collective_birthday(birthdates, today=None):
    """
    Returns [collective_years_float, next_collective_birthday_date]
    
    Logic:
    - Each real day every family member ages 1 day → total family-days lived = sum of individual ages
    - One collective year = 365.2425 family-days
    - More members → collective birthday arrives faster because remaining family-days are divided by n
    """
    if today is None:
        today = date.today()

    n = len(birthdates)
    if n == 0:
        return [0.0, today]

    # Calculate individual ages in real days
    individual_days_lived = [(today - b).days for b in birthdates]

    # Total family-days lived (sum of all individual days lived)
    total_family_days = sum(individual_days_lived)

    # Collective age in years (float)
    collective_years = total_family_days / REAL_YEAR_DAYS

    # Family-days already used in the current collective year
    family_days_into_current_year = total_family_days % REAL_YEAR_DAYS

    # Family-days still needed to complete the current collective year
    family_days_remaining = REAL_YEAR_DAYS - family_days_into_current_year

    # Convert remaining family-days to real calendar days
    # (this is where the speed-up happens: more members → fewer real days needed)
    real_days_until_next = family_days_remaining / n

    # If we are effectively on the birthday today, schedule the next one
    if real_days_until_next < 0.1:
        real_days_until_next = REAL_YEAR_DAYS / n

    # Date of the next collective birthday
    next_birthday = today + timedelta(days=real_days_until_next)

    return [collective_years, next_birthday]