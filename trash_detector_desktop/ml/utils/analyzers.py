"""
Алгоритмы для анализирования детекций YOLO.
"""


from typing import Optional

import numpy as np


def softmax(x: list) -> float:
    """"""
    return np.exp(x) / sum(np.exp(x))


def _recalculation_dict_summator(summator: dict) -> dict:
    """Перерасчёт аналитического словаря в вероятностном виде."""
    conf_list = softmax(list(summator.values()))
    for i, key in enumerate(summator.keys()):
        summator[key] = conf_list[i]
    return summator


def analyse_target_class_by_conf(
        classes: list,
        conf: list,
) -> tuple[Optional[str], Optional[float]]:
    """Обобщение класса изображения по наибольшему conf.
    return:
        best_class: Optional[str] - самый вероятный класс.
        best_conf: Optional[float] - вероятность итогового класса."""
    summator = {}
    for i in range(len(classes)):

        name_class = str(classes[i])
        if name_class not in summator:
            summator[name_class] = conf[i]
        else:
            summator[name_class] += conf[i]

    summator = _recalculation_dict_summator(summator)
    best_class = max(summator, key=summator.get) if summator else None
    best_conf = summator.get(best_class, None)
    return (best_class, best_conf)


def analyse_target_class_by_count(
        classes: list,
        conf: list = None,
) -> tuple[Optional[str], Optional[float]]:
    """Обобщение класса изображения по наибольшему количеству.
    return:
        best_class: Optional[str] - самый вероятный класс.
        best_conf: Optional[float] - вероятность итогового класса."""
    summator = {}
    for i in range(len(classes)):

        name_class = str(classes[i])
        if name_class not in summator:
            summator[name_class] = 1
        else:
            summator[name_class] += 1

    summator = _recalculation_dict_summator(summator)
    best_class = max(summator, key=summator.get) if summator else None
    best_conf = summator.get(best_class, None)
    return (best_class, best_conf)


def analyse_target_class_without_changes(
        classes: list,
        conf: list,
) -> tuple[list, list]:
    """Возвращаем абсолютно все классы, которые были предсказаны моделью.
    return:
        classes: list - все предсказанные классы моделью.
        conf: list - все верояности предсказанные моделью."""
    return (classes, conf)
