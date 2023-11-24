import argparse
import subprocess


def generate_ui_file(file_name, new_path):
    command = " ".join(["pyuic6", file_name, "-o", new_path])
    print(command)
    subprocess.call(command, shell=True)


def generate_ui_resources(resource_file, file_path):
    new_file_name = resource_file[:resource_file.find(".")]
    command = " ".join(["pyside6-rcc", resource_file, "|", "sed", "'0,/PySide6/s//PyQt6/'", ">" f"{file_path}{new_file_name}.py"])
    print(command)
    subprocess.call(command, shell=True)


def main():
    parser = argparse.ArgumentParser(
        description="Сбор параметров для генерации *.ui и *.qrc файлов",
    )
    parser.add_argument(
        "path",
        type=str,
        help="Относительный путь к директории с / в конце",
    )
    parser.add_argument(
        "-i",
        type=str,
        help="Указание файла, который нужно импортировать в свеже сгенерированном .ui файле",
    )
    args = parser.parse_args()
    ui_files = [
        "main_window.ui",
    ]
    qrc_resources = [
        "resources.qrc",
    ]
    for ui_file in ui_files:
        new_file_name = ui_file[:ui_file.find(".")]
        new_path = f"{args.path}{new_file_name}.py"
        generate_ui_file(ui_file, new_path)
        if args.i:
            add_string = f"from . import {args.i}\n"
            with open(new_path, "r+") as file:
                lines = file.readlines()
                file.write("")
                file.seek(0)
                for index, line in enumerate(lines):
                    if "from PyQt6" in line:
                        lines.insert(index+1, "\n")
                        lines.insert(index+2, add_string)
                        break
                file.writelines(lines)

    for qrc_file in qrc_resources:
        generate_ui_resources(qrc_file, file_path=args.path)
    print("Don't forget import converted .qrc in converted .ui file")


if __name__ == "__main__":
    main()
