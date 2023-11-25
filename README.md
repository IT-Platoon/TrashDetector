# Trash-Detector-Desktop

## Присутствует уже собранная версия приложения. Она доступна по ссылке: https://github.com/IT-Platoon/TrashDetector/releases/latest

## Исходные данные

### Датасеты и веса: https://drive.google.com/drive/folders/1N4Dv6JZApnSa5WUZA-FRq5hyIRXjP0rO?usp=sharing

### Так же присутствует модель для использования в ```trash_detector_desktop/ml/weights```

## Установка

Установка производилась на OS Linux Manjaro Gnome

1. Настройка виртуального окружения
```bash
make install_linux
```

2. Запуск приложения
```bash
make run
```

3. Сборка приложения локально
```bash
make build_linux
```

4. Для использования собранного приложения:
```bash
make run_prod
```

Также присутствует версия для сборки на OS Windows

1. Настройка виртуального окружения
```bash
make build_windows
```

## Используемые технологии

- Python - язык программирования
- PyQt - библиотека для разработки интерфейса
- ultralytics - нейросеть для выделения объекта на изображении
