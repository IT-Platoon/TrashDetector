"""
Алгоритмы для логов детектирования.
"""


import os
import csv
import pandas as pd


def update_logfile(
        logfile_name: str,
        info: str,
        target: str,
) -> None:
    """Создание/дополнение лог-файла."""
    df = pd.DataFrame({'info': [info], 'target': [target]})
    if not os.path.isfile(logfile_name):
        df.to_csv(logfile_name, index=False, quoting=csv.QUOTE_NONE, escapechar="\0", encoding="utf-8-sig")
    else:
        df.to_csv(logfile_name, mode='a', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\0', encoding = "utf-8-sig")
