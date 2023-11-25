"""
Алгоритмы для логов детектирования.
"""


import os
import csv
import pandas as pd


def update_logfile(
    logfile_name: str,
    info: str,
    target_class: str,
    target_conf: float,
) -> None:
    """Создание/дополнение лог-файла."""
    df = pd.DataFrame({'info': [info], 'target_class': [target_class], 'target_conf': target_conf})
    if not os.path.isfile(logfile_name):
        df.to_csv(logfile_name, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(logfile_name, mode='a', index=False, header=False, encoding="utf-8-sig")
