# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
pip install -r requirements.txt
```
### Setup
Make sure to follow the steps in CrowdNav project Readme for building the [CrowdNav](https://github.com/karola65/foas_crowd_nav) docker image 

### Run unit tests
To run our CrowdNav tests, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.your_exemplar.test_your_exemplar_interface
```

### To run baseline - random actions

In a terminal, switch to the branch **baseline** and navigate to the parent folder of the project and issue:
```
python run.py
```
This runs the baseline without any adaptation strategy. 


### To run with adaptation strategy

In a terminal, switch to the branch **training** and navigate to the parent folder of the project and issue:
```
python run.py
```
This runs the baseline with the adaptation strategy added for the analyser and planner. If you would like to run the strategy for different traffic levels, change the number of cars in CrowdNav project config file and build the docker image again as explained in CrowdNav Readme.

### Results

- For accessing the Q-tables check the .csv files in the paretn folder of training branch
- For accessing the results of the tests with the adaptation strategy check the .json files in the paretn folder of training branch and the baseline runs, check the .json files in the paretn folder of testing branch

