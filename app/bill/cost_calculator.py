def calculate_ac_bill(usage_seconds):
    hours = usage_seconds/3600
    units_consumed = hours * 1.05

    if units_consumed <= 50:
        total_cost = units_consumed * 4.10
    elif units_consumed <= 100:
        total_cost = (50 * 4.10) + ((units_consumed - 50) * 5.55)
    elif units_consumed <= 200:
        total_cost = (50 * 4.10) + (50 * 5.55) + ((units_consumed - 100) * 7.10)
    else:
        total_cost = (50 * 4.10) + (50 * 5.55) + (100 * 7.10) + ((units_consumed - 200) * 8.15)

    total_cost = round(total_cost, 2)

    return hours,total_cost