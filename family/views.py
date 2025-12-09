from datetime import date, datetime
from django.shortcuts import render
from django.http import JsonResponse
from family.config_data.family_settings import birthdates
from family.utils.birthday import get_family_collective_birthday


def birthday_page(request):
    return render(request, 'family/age.html')

def api_birthday_data(request):
    collective_years, next_bday = get_family_collective_birthday(birthdates)

    data = {
        "collective_years": int(collective_years),
        "collective_years_float": round(collective_years, 4),
        "next_birthday": next_bday.strftime('%Y-%m-%d'),
        "is_today": next_bday == date.today(),
        "family_size": len(birthdates),
        "days_until_next": (next_bday - date.today()).days,
        "updated_at": date.today().isoformat(),
    }

    return JsonResponse(data)