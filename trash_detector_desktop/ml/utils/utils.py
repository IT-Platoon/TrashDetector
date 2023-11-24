"""
Алгоритмы инструментов для ML.
"""

from typing import Union
import os
from datetime import datetime

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
from ultralytics import YOLO


def load_model(path: str) -> YOLO:
    """ Загрузка модели.
    return: model """

    cuda_flag = torch.cuda.is_available()
    device = 'cuda' if cuda_flag else 'cpu'
    print(device)

    model = YOLO(path).to(device)
    return model


def get_directory_name(detection_type: str) -> str:
    """Создание датированого названия новой директории."""
    bad_symbols = (" ", ".", ":")
    now_datetime = []
    for symbol in str(datetime.now()):
        now_datetime.append(
            symbol if symbol not in bad_symbols else "-"
        )
    return f"detection_{detection_type}_{''.join(now_datetime)}"


def list_to_str(value: Union[list, str]) -> str:
    """Преобразование списка в строку."""
    if isinstance(value, list):
        value = f"[{', '.join(value)}]"
    return value


def mkdir(dir_save: str) -> None:
    """Создание директории, если ещё не создана."""
    if not os.path.isdir(dir_save):
        os.mkdir(dir_save)


def save_imgs(list_final_dict: list[dict], dir_save: str) -> list[dict]:
    """ Сохранение всех предсказанных изображений с боксами.
    list_final_dict: list[dict] - предсказанные данные.
    dir_save: str - директория, в которую сохранить предсказанные изображения.
    return: list[dict] """

    for final_dict in list_final_dict:
        filename = os.path.basename(final_dict["filename"])
        path = os.path.join(dir_save, filename)
        final_dict["path"] = path
        image = cv2.cvtColor(final_dict["img"], cv2.COLOR_BGR2RGB)
        pixels = np.array(image)
        plt.imsave(path, pixels)
    return list_final_dict


def convert_images_to_video(
        images: list[np.ndarray],
        filename: str,
        fps: int = 24,
) -> cv2.VideoWriter:
    """ Соединение изображений в одно видео.
    images: np.array - массив изображений.
    filename: str - название выходного файла.
    return - видео """
    img = images[0]
    height = img.shape[0]
    width = img.shape[1]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    for img in images:
        video.write(img)

    video.release()
    return video
