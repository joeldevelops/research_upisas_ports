# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites
Tested with Python 3.10.12

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
pip install -r requirements.txt
```
## Docker Image
In the root directory of the repository, you can run the following command to build the docker image containing the BSN exemplar:
```
docker build --tag bsn_proj .
```

### Run unit tests
In a terminal, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.upisas.test_exemplar
python -m UPISAS.tests.upisas.test_strategy
python -m UPISAS.tests.swim.test_swim_interface

python -m UPISAS.tests.your_exemplar.test_your_exemplar_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```
