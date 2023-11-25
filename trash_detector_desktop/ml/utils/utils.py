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

import supervision as sv
from supervision.draw.color import ColorPalette


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


def create_beautiful_bbox(
    model,
    results,
    box_annotator: sv.BoxAnnotator
):
    """"""
    if isinstance(results, list):
        result = results[0]
    else:
        result = results

    scene = result.orig_img
    detections = sv.Detections.from_ultralytics(result)
    labels = [
        f"{model.names[class_id]} {confidence:0.2f}"
        for _, _, confidence, class_id, _
        in detections
    ]

    # Дальше код скопирован из либы supervision с фиксом для русского:

    font = cv2.FONT_HERSHEY_COMPLEX
    for i in range(len(detections)):
        x1, y1, x2, y2 = detections.xyxy[i].astype(int)
        class_id = (
            detections.class_id[i] if detections.class_id is not None else None
        )
        idx = class_id if class_id is not None else i
        color = (
            box_annotator.color.by_idx(idx)
            if isinstance(box_annotator.color, ColorPalette)
            else box_annotator.color
        )
        cv2.rectangle(
            img=scene,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=color.as_bgr(),
            thickness=box_annotator.thickness,
        )

        text = (
            f"{class_id}"
            if (labels is None or len(detections) != len(labels))
            else labels[i]
        )

        text_width, text_height = cv2.getTextSize(
            text=text,
            fontFace=font,
            fontScale=box_annotator.text_scale,
            thickness=box_annotator.text_thickness,
        )[0]

        text_x = x1 + box_annotator.text_padding
        text_y = y1 - box_annotator.text_padding

        text_background_x1 = x1
        text_background_y1 = y1 - 2 * box_annotator.text_padding - text_height

        text_background_x2 = x1 + 2 * box_annotator.text_padding + text_width
        text_background_y2 = y1

        cv2.rectangle(
            img=scene,
            pt1=(text_background_x1, text_background_y1),
            pt2=(text_background_x2, text_background_y2),
            color=color.as_bgr(),
            thickness=cv2.FILLED,
        )
        cv2.putText(
            img=scene,
            text=text,
            org=(text_x, text_y),
            fontFace=font,
            fontScale=box_annotator.text_scale,
            color=box_annotator.text_color.as_rgb(),
            thickness=box_annotator.text_thickness,
            lineType=cv2.LINE_AA,
        )
    return scene
