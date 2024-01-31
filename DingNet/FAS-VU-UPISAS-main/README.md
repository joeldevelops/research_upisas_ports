# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
pip install -r requirements.txt
```
### Run unit tests
In a terminal, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.upisas.test_exemplar
python -m UPISAS.tests.upisas.test_strategy
python -m UPISAS.tests.swim.test_swim_interface
```
#### DingNet
First, build the DingNet docker image. To do so, please follow the build instructions from the [DingNet repo](https://github.com/Woutuuur/FAS-VU-DingNet)'s README.
Once the image is built, run the following command:
```
python -m UPISAS.tests.dingnet.test_dingnet_interface
```

### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```

This will run 100 iterations of the DingNet simulation first with adaptation and then without adaptation.
If you want to visually see the adaptation open http://localhost:6901/ in a browser window and login with `kasm_user:password`.
Once both runs are done the results are presented using various plots.
