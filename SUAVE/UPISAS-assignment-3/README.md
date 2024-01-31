# UPISAS
Unified Python interface for self-adaptive system exemplars.

> [!WARNING]  
> This repository has been updated for the FAS course in VU. For the latest documentation of installation and development, 
> please refer to [DOCUMENTATION.md](https://github.com/caesarw/UPISAS/blob/assignment-3/DOCUMENTATION.md) for documentations. 
> 
> Please refer to [HOWTO.md](https://github.com/caesarw/UPISAS/blob/assignment-3/HOWTO.md) for how-tos. 

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

python -m UPISAS.tests.your_exemplar.test_your_exemplar_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```


