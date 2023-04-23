def calculate_air_quality(tvoc, co2):
    if tvoc <= 220:
        tvoc_iaqi = tvoc/220 * 50
    elif tvoc <= 660:
        tvoc_iaqi = (tvoc - 220)/440 * (100 - 51) + 51
    elif tvoc <= 2200:
        tvoc_iaqi = (tvoc - 660)/1540 * (150 - 101) + 101
    elif tvoc <= 5500:
        tvoc_iaqi = (tvoc - 2200)/3300 * (200 - 151) + 151
    elif tvoc <= 11000:
        tvoc_iaqi = (tvoc - 5500)/5500 * (300 - 201) + 201
    else:
        tvoc_iaqi = (tvoc - 11000)/44000 * (500 - 301) + 301

    if co2 <= 1000:
        co2_iaqi = co2/1000 * 50
    elif co2 <= 2000:
        co2_iaqi = (co2 - 1000)/1000 * (100 - 51) + 51
    elif co2 <= 5000:
        co2_iaqi = (co2 - 2000)/3000 * (150 - 101) + 101
    elif co2 <= 10000:
        co2_iaqi = (co2 - 5000)/5000 * (200 - 151) + 151
    else:
        co2_iaqi = (co2 - 10000)/5000 * (300 - 201) + 201

    iaqi = max(tvoc_iaqi, co2_iaqi)
    return round(iaqi)
