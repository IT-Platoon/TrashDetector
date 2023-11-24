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
        df.to_csv(logfile_name, index=False, quoting=csv.QUOTE_NONE, escapechar="\0")
    else:
        df.to_csv(logfile_name, mode='a', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\0')


def create_submission_csv(
    filename_csv: str,
    list_final_dict: list[dict],
    dir_save: str,
) -> None:
    """ Создание submission csv-файла.
    filename_csv: str - название csv файла.
    list_final_dict: list[dict] - список предсказанных изображений.
    dir_save: str - директория сохранения.
    return: None """

    list_filename = []
    list_target = []

    # Определяю target каждого изображения.
    for final_dict in list_final_dict:

        list_filename.append(final_dict['filename'])
        target_class = final_dict['target_class']

        # Классы для отправки решения хакатона.
        # TODO: нужно поменять классы!
        if target_class in (,):
            target_class = 1
        else:
            target_class = 0

        list_target.append(target_class)

    # Корректирую названий файлов и оставляю их без директории.
    # TODO: возможно нужно менять удаление директории!
    new_list_filename = []
    for elem in list_filename:
        try:
            testing = elem.split("/")[-1]
            new_list_filename.append(testing)
        except ValueError:
            testing = elem
            new_list_filename.append(testing)

    df = pd.DataFrame({'name': new_list_filename, 'class': list_target})

    # TODO: возможно нужно менять параметр 'sep'!
    df.to_csv(os.path.join(dir_save, filename_csv), sep=";", index=False)
