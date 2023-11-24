set APPLICATION_NAME=trash_detector

goto %1

:install
  python -m venv venv
  call "venv/Scripts/activate.bat"
  pip install -Ur requirements.txt
  pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
	pip install ultralytics
	pip install dill
goto end
  
:build
  call "venv/Scripts/activate.bat"
  pyinstaller %APPLICATION_NAME%.spec
  cp -r ./venv/Lib/site-packages/ultralytics ./dist/%APPLICATION_NAME%/%APPLICATION_NAME%
  cp -r ./venv/Lib/site-packages/dill ./dist/%APPLICATION_NAME%/%APPLICATION_NAME%
goto end

:install_web
  python -m venv venv
  call "venv/Scripts/activate.bat"
  pip install -Ur requirements_web.txt
  cp -r ./trash_detector_desktop/ml/weights/best.pt ./trash_detector_web
goto end
  
:run_web
  call "venv/Scripts/activate.bat"
  cd trash_detector_web
  uvicorn main:app
goto end
  
:end
