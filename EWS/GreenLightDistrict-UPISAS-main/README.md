# Team: 2_4_Emergent Web Server
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
python3 -m UPISAS.tests.upisas.test_exemplar
python3 -m UPISAS.tests.upisas.test_strategy
python3 -m UPISAS.tests.swim.test_swim_interface

python3 -m UPISAS.tests.your_exemplar.test_your_exemplar_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python3 run.py
```

### Possible issues
We put some sleep for ews to start running properly (including client script) at the beginning of every test. The sleep time was sufficient for Ubuntu but might not be for other operating systems. Please check the comments in `start_run` function of `EWS` in the `UPISAS/exemplars/your_exemplar.py` and also in `_start_server_and_wait_until_is_up` function in the `UPISAS/tests/your_exemplar/test_your_exemplar_interface.py` file.


### Folder Structure
- **data**
    - `compositions.csv`: contains the compositions of each configuration broken down into 4 key components (request handler, http handler, compression, cache handler)
    - `train_data.csv`: contains the data collected for a few specific client combinations applied on each of the configurations.
    - `train_data_with_comp.csv`: contains the data from the previous two files merged together.
- **results**: contains three csv files generated for evaluating three different adaptation strategies in the same test scenarios.
- **utils**
    - `data_collection.py`: code used for generating `train_data.csv` which can be run to recreate the dataset or modified to collect data for more client combinations.
    - `extract_comp.py`: code used for generating `compositions.csv` and merging it with the collected train data.
    - `result_visualization.py`: code used for generating visualizations (charts) for the evaluation of different adaptation strategies in different scenarios.
- **graphs**: contains line charts and bar charts generated for the comparative evaluation of different adaptation strategies.

(Note: The analyze phase uses a threshold to decide on configuration changes. This part may need adjustments on MacOS, as EWS tends to run slower on MacOS. It might be necessary to lower the threshold values for proper performance on these systems.)
