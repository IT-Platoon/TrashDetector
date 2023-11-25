# Trash-Detector-Web

## Исходные данные

### Датасеты и веса: https://drive.google.com/drive/folders/1N4Dv6JZApnSa5WUZA-FRq5hyIRXjP0rO?usp=sharing

### Так же присутствует модель для использования в ```trash_detector_desktop/ml/weights``` и в ```trash_detector_web```

## Установка

Установка производилась на OS Linux Manjaro Gnome

1. Настройка виртуального окружения
```bash
make install_linux_web
```

2. Запуск приложения
```bash
make run_linux_web
```

Так же есть команды для установки на ОS Windows

1. Настройка виртуального окружения
```bash
make install_windows_web
```

2. Запуск приложения
```bash
make run_windows_web
```

## Используемые технологии

- Python - язык программирования
- FastAPI - библиотека для написания API
- aiortc - библиотека для создания RTC соединения
- ultralytics - нейросеть для выделения объекта на изображении
