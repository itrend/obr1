#!/usr/bin/env python3
from datetime import date, timedelta
import re
import sys

from total_comp import TOTAL_COMP
import config

TXT_DIR = "."
TEMPLATE = f"{TXT_DIR}/template.txt"
FILE_PREFIX = "Empl_"


WORKING_DAYS = {
    # https://kik-info.com/spravochnik/calendar/2024/
    2024: {
        1: 22,
        2: 21,
        3: 20,
        4: 22,
        5: 19,
        6: 20,
        7: 23,
        8: 22,
        9: 19,
        10: 23,
        11: 21,
        12: 19,
    },
    # https://kik-info.com/spravochnik/calendar/2025/
    2025: {
        1: 22,
        2: 20,
        3: 20,
        4: 20,
        5: 19,
        6: 21,
        7: 23,
        8: 21,
        9: 20,
        10: 23,
        11: 20,
        12: 20,
    },
}


def main():
    check_config()

    argc = len(sys.argv)
    today = date.today()
    month = int(sys.argv[1]) if argc > 1 else today.month
    year = int(sys.argv[2]) if argc > 2 else today.year
    if argc == 1:
        # if nothing passed - previous month
        pm = today.replace(day=1) - timedelta(days=1)
        month, year = pm.month, pm.year
    for_month(month, year)


def for_month(month: int, year: int):
    days_in_month = WORKING_DAYS[year][month]
    amount = TOTAL_COMP.get(year, {}).get(month, 0.0)
    output_file_name = f"{TXT_DIR}/{FILE_PREFIX}{config.EIK}_{year}_{month:02d}.txt"

    print(f"Пиша файл за {year}-{month:02d}, {days_in_month} работни дни: {output_file_name}")
    if amount == 0.0:
        print(f"Няма месечен облагаем доход, пиша 0.0 в поле 31 (виж total_comp.py)")

    egn = config.EGN.encode("ascii")
    eik = config.EIK.encode("ascii")
    family_name = config.FAMILY_NAME.upper().encode("cp1251")
    initials = config.INITIALS.upper().encode("cp1251")

    def replace(row: bytes):
        return (row
                .replace(b'{{YEAR}}', b"%d" % year)
                .replace(b'{{MONTH1}}', b"%d" % month)
                .replace(b'{{DAYS}}', b"%02d" % days_in_month)
                .replace(b'{{AMOUNT}}', b"%.2f" % amount)
                .replace(b'{{EGN}}', egn)
                .replace(b'{{EIK}}', eik)
                .replace(b'{{FAMILY_NAME}}', family_name)
                .replace(b'{{INITIALS}}', initials)
               )

    with (open(TEMPLATE, "rb") as in_file,
          open(output_file_name, "wb") as out_file):
        out_file.writelines(replace(row) for row in in_file.readlines())


def check_config():
    assert re.fullmatch(r"\d+", config.EGN), "Грешно/непопълнено ЕГН"
    assert re.fullmatch(r"\d+", config.EIK), "Грешно/непопълнено ЕИК"
    assert "?" not in config.FAMILY_NAME, "Не си променил фамилията"
    assert "?" not in config.INITIALS, "Сложи инициали"
    return config


if __name__ == "__main__":
    main()
