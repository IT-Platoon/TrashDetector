APPLICATION_NAME = trash_detector_desktop


install_linux_dev: ##@Application Create Virtual Enviroment and Install Requirements on Linux for dev
	python -m venv venv && \
	. ./venv/bin/activate && \
	pip install -Ur requirements.dev.txt

install_linux: ##@Application Create Virtual Enviroment and Install Requirements on Linux
	python -m venv venv && \
	. ./venv/bin/activate && \
	pip install -Ur requirements.txt && \
	pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu && \
	pip install ultralytics && \
	pip install dill

install_windows: ##@Application Create Virtual Enviroment and Install Requirements on Windows
	./build.bat install

format:  ##@Code Reformat code with isort and flake8
	python3 -m isort $(APPLICATION_NAME) --settings-file=./setup.cfg
	python3 -m flake8 $(APPLICATION_NAME) --config=./setup.cfg

run:  ##@Application Run application
	python3 -m $(APPLICATION_NAME)

run_prod:   ##@Application Run build application
	./dist/$(APPLICATION_NAME)/$(APPLICATION_NAME)_app

convert:  ##@Code convert .ui files and .qrc files in .py
	cd ./$(APPLICATION_NAME)/qt && python auto_generate_files.py "../forms/" -i "resources"

build_linux:  ##@Code build in Application with Pyinstaller on Linux
	make install_linux && \
	. ./venv/bin/activate && \
	pyinstaller $(APPLICATION_NAME).spec && \
	cp -r ./venv/lib/python3.10/site-packages/ultralytics ./dist/$(APPLICATION_NAME)/$(APPLICATION_NAME)
	cp -r ./venv/lib/python3.10/site-packages/dill ./dist/$(APPLICATION_NAME)/$(APPLICATION_NAME)

build_windows:  ##@Code build in Application with Pyinstaller on Windows
	make install_windows && \
	./build.bat build

clean:  ##@Code Clean directory from garbage files
	sudo rm -fr *.pyc *.egg-info dist build venv


install_windows_web:
	./build.bat install_web

run_windows_web:
	./build.bat run_web

install_linux_web:
	python -m venv venv && \
	. ./venv/bin/activate && \
	pip install -Ur requirements_web.txt

run_linux_web:
	. ./venv/bin/activate && \
	cd ./trash_detector_web && \
	python3 -m uvicorn main:app
