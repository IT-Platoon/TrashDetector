"""
Api для работы с готовыми моделями.
"""

import os
from datetime import datetime
from typing import Callable

import cv2
from ultralytics import YOLO

from .utils import *


class InferenceAPI:
    """Получение результатов моделей."""

    def __init__(
        self,
        model: YOLO | str,
        conf: float = 0.25,
        iou: float = 0.7,

        box_thickness: int = 2,
        text_thickness: int = 1,
        text_scale: float = 0.7,
    ):
        if isinstance(model, YOLO):
            self.model = model
        elif isinstance(model, str):
            self.model = load_model(model)

        self.conf = conf
        self.iou = iou

        self.box_annotator = sv.BoxAnnotator(
            thickness=box_thickness,
            text_thickness=text_thickness,
            text_scale=text_scale,
        )

    def predict_one(
        self,
        filename: str,
        analyzer: Callable[[list, list], Optional[tuple]] = analyse_target_class_by_count,
    ) -> dict:
        """ Предсказание.
        filename: str - путь или url до одного изображения.

        return: dict - результат предсказания в формате
        {
            'filename': str,  # Название изображения.
            'classes': list,  # Классы, которые имеются на изображении.
            'count': int,  # Кол-во объектов на изображении.
            'target_class': Union[str, list],  # Предсказанный класс для картинки.
            'conf': Union[float, list],  # Достоверность предсказанного класса.
            'img': Image  # Изображение с боксами объектов.
        }
        """
        model = self.model

        # Делаю предсказание.
        result = model.predict(filename, conf=self.conf, iou=self.iou, verbose=False)[0]

        # Преобразую результат в изображение с box.
        img = create_beautiful_bbox(model, result, self.box_annotator)
        # img = result.plot()

        # Получаю классы, которые есть на изображении.
        classes = []
        for i in result.boxes.cls:
            classes.append(model.names[int(i)])
        # Достоверность предсказания того или иного класса.
        conf = []
        for i in result.boxes.conf:
            conf.append(i)
        # Количество лебедей на изображении.
        count = len(classes)

        # Предсказанный класс для картинки.
        target_class, conf = analyzer(classes, conf)

        # Результат предсказания хранится тут.
        final_dict = {
            'filename': filename,
            'classes': classes,
            'count': count,
            'target_class': target_class,
            'conf': conf,
            'img': img,
        }
        return final_dict

    def run_detection_images(
        self,
        list_filenames: list[str],
        dir_save: str,
        analyzer: Callable[[list, list], Optional[str]] = analyse_target_class_by_count,
        logfile_name: str = 'logfile.csv',  # .csv
    ) -> list[dict]:
        """Запуск обработки изображений."""
        mkdir(dir_save)

        dir_name = get_directory_name("images")
        dir_save = os.path.join(dir_save, dir_name)
        mkdir(dir_save)

        logfile_name = os.path.join(dir_save, logfile_name)

        list_final_dict = []
        for i, filename in enumerate(list_filenames):
            final_dict = self.predict_one(filename, analyzer=analyzer)

            # Сохранение лог-файла.
            target = list_to_str(final_dict['target_class'])
            update_logfile(logfile_name, final_dict['filename'], target)

            list_final_dict.append(final_dict)
            frame = cv2.resize(
                final_dict["img"],
                dsize=(640, 640),
                interpolation=cv2.INTER_CUBIC,
            )
            yield i * 100 / len(list_filenames), frame

        # Сохранение изображения.
        list_final_dict = save_imgs(list_final_dict, dir_save)
        return list_final_dict

    def run_detection_videos(
        self,
        list_filenames: list[str],
        dir_save: str,
        logfile_name: str = 'logfile.csv',  # .csv
        fps_video_save: int = 24,
        flag_realtime_show_video: bool = True,
    ) -> list[dict]:
        """Запуск обработки видео.

        return: list[dict] - результат, где словарь имеет следующий вид:
        {
            'filename': str,  # Название обработанного видео.
            'path': str,  # Путь до обработанного видео..
        }
        """
        model = self.model
        mkdir(dir_save)

        paths = []
        for index, filename in enumerate(list_filenames):
            cap = cv2.VideoCapture(filename)
            # Папка для сохранения одного видео.
            tmp_filename = filename.split('/')[-1].replace('.', '_')
            dir_name = get_directory_name(f"video_{tmp_filename}")
            dir_name = os.path.join(dir_save, dir_name)
            os.mkdir(dir_name)
            # Файл для логов.
            logfile_name_i = os.path.join(dir_name, logfile_name)

            count_frame = 0
            lst_images = []
            while cap.isOpened():
                count_frame += 1
                # Считываем кадр
                success, frame = cap.read()
                if success:
                    results = model.predict(frame, conf=self.conf, iou=self.iou, verbose=False)
                    annotated_frame = create_beautiful_bbox(model, results[0], self.box_annotator)
                    # annotated_frame = results[0].plot()
                    lst_images.append(annotated_frame)

                    classes = []
                    for i in results[0].boxes.cls:
                        classes.append(model.names[int(i)])

                    # Логгируем найденные объекты на видео.
                    if len(classes) != 0:
                        info = f'{count_frame // fps_video_save} sec'
                        classes = list_to_str(classes)
                        update_logfile(logfile_name_i, info, classes)

                    if flag_realtime_show_video:
                        # Изменяю изображение для корректного отображения.
                        annotated_frame = cv2.resize(
                            annotated_frame,
                            dsize=(640, 640),
                            interpolation=cv2.INTER_CUBIC,
                        )
                        yield index * 100 / len(list_filenames), annotated_frame
                        # cv2.imshow("Detection result. Exit `q`", annotated_frame)

                        # # Остановка по нажатию 'q'
                        # if cv2.waitKey(1) & 0xFF == ord("q"):
                        #     break
                else:
                    break  # Конец видео

            filename = filename.split('/')[-1]
            format_video = filename[-3:]
            filename = f'{filename[:-4]}_annot.{format_video}'
            path = os.path.join(dir_name, filename)
            item = {
                "filename": filename,
                "path": path,
            }
            paths.append(item)

            # Сохранение видео.
            convert_images_to_video(lst_images, path, fps=fps_video_save)

            # Закрытие окна
            cap.release()
            cv2.destroyAllWindows()
        return paths

    def run_detection_webcam(
        self,
        source_webcam: int,
        dir_save: str,
        logfile_name: str = 'logfile.csv',  # .csv
        flag_save_imgs: bool = False,
        flag_realtime_show_video: bool = True,
    ) -> None:
        """Запуск детектирования в реальном времени по веб-камере."""
        model = self.model
        mkdir(dir_save)

        dir_name = get_directory_name(f'camera{source_webcam}')
        dir_save = os.path.join(dir_save, dir_name)
        os.mkdir(dir_save)
        logfile_name = os.path.join(dir_save, logfile_name)
        go_next = True
        for results in model.predict(source_webcam, stream=True, conf=self.conf, iou=self.iou, verbose=False):
            if not go_next:
                model.predictor.dataset.close()
                break

            classes = []
            if len(results) != 0:
                for result in results:
                    for i in result.boxes.cls:
                        classes.append(model.names[int(i)])

                # Логгируем найденные объекты с вебкамеры.
                if len(classes) != 0:
                    datetime_now = datetime.now()
                    datetime_now = str(datetime_now)[:19].replace(':', '-')
                    str_classes = list_to_str(classes)
                    update_logfile(logfile_name, datetime_now, str_classes)

                    # Сохранение кадров, на котором был найден объект.
                    if flag_save_imgs:
                        path = os.path.join(dir_save, datetime_now + '.jpg')
                        image = create_beautiful_bbox(model, results, self.box_annotator)
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        image = np.array(image)
                        plt.imsave(path, image)

            if flag_realtime_show_video:
                # Изменяю изображение для корректного отображения.

                frame = create_beautiful_bbox(model, results, self.box_annotator)
                # frame = results.plot()
                frame = cv2.resize(
                    frame,
                    dsize=(640, 640),
                    interpolation=cv2.INTER_CUBIC,
                )
                go_next = yield frame, classes
                # cv2.imshow("Detection result. Exit `q`", frame)
                # # Остановка по нажатию 'q'
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     return


if __name__ == '__main__':
    inference = InferenceAPI('./weights/best.pt')

    list_image_filenames = os.listdir('./demo_dataset/images')
    list_image_filenames = [f'./demo_dataset/images/{i}' for i in list_image_filenames]
    list_video_filenames = ['./demo_dataset/videos/3654189_20sec.mp4']

    dir_save = './temp_results'

    # detection = inference.run_detection_videos(list_video_filenames, dir_save, flag_realtime_show_video=False)
    # try:
    #     next(detection)
    # except StopIteration as exception:
    #     pass

    # detection = inference.run_detection_images(list_image_filenames, dir_save)
    detection = inference.run_detection_webcam(0, dir_save, flag_save_imgs=False)
    try:
        yielded = next(detection)
        while True:
            yielded = detection.send(True)
    except StopIteration as exception:
        pass
