# CrowdNav

![Banner](https://raw.githubusercontent.com/Starofall/CrowdNav/master/banner.PNG)


### Description
CrowdNav is a simulation based on SUMO and TraCI that implements a custom router
that can be configured using kafka messages or local JSON config on the fly while the simulation is running.
Also runtime data is send to a kafka queue to allow stream processing and logger locally to CSV.

## Minimal setup for HTTP solution for running CrowdNav
1. Clone our CrowdNav repository 
```
git clone https://github.com/karola65/foas_crowd_nav.git
```
2. Get Docker running on your OS 
3. The next step is to navigate to the parent directory of the cloned CrowdNav project and build the Docker image

* Run 
```
docker build -t crowd-nav-local .
``` 
to build the docker image
* Then run 
```
docker run -p 3000:3000 -it crowd-nav-local
```
to start the container

4. Now our CrowdNav is running in port `3000`

### For testing the HTTP endpoints of CrowdNav
1. For monitoring CrowdNav values
  ```
  GET localhost:3000/monitor
  ```
2. To check the JSON schema of monitor
  ```
  GET localhost:3000/monitor_schema
  ```
3. For checking the adaptation options
  ```
  GET localhost:3000/adaptation_options
  ```
4. To check the JSON schema of adaptation options
  ```
  GET localhost:3000/adaptation_options_schema
  ```
5. To execute some adaptation 
  ```
  PUT localhost:3000/execute
  ```
  with an example request body: 
  ```
  {"routeRandomSigma": 0.0,"explorationPercentage": 0.0,"maxSpeedAndLengthFactor": 1,"averageEdgeDurationFactor": 1,"freshnessUpdateFactor": 10,"freshnessCutOffValue": 90,"reRouteEveryTicks": 60}
  ```

6. To check the JSON schema of execute
  ```
  GET localhost:3000/execute_schema
  ```


### For testing HTTP-Based solution with UPISAS
1. Clone our CrowdNav repository 
```
git clone https://github.com/karola65/foas_crowd_nav.git
```
2. Clone also our UPISAS repository 
```
git clone https://github.com/karola65/foas_upisas.git
```
3. Get Docker running on your OS 
4. The next step is to navigate to the parent directory of the cloned CrowdNav project and build the Docker image

* Run 
```
docker build -t crowd-nav-local .
``` 
to build the docker image

5. Next, we go to the parent directory of the cloned UPISAS in a terminal and execute
```
pip install -r requirements.txt
```
6. Still in the parent directory, now let’s run our exemplar tests 
```
python -m UPISAS.tests.your_exemplar.test_your_exemplar_interface
```
7. Before running the tests, please make sure there is no container with the name - “upisas-crowdnav” of our image running, if so please delete it.

Now all our tests run and pass.


### Minimal setup Kafka Based

* Install [Kafka](https://kafka.apache.org/) (we recommend [this](https://hub.docker.com/r/spotify/kafka/) Docker image) and set kafkaHost in Config.py
* Run `python run.py`

### Getting Started Guide
A first guide on how to use (i.e. adapt, measure, optimize) CrowdNav with the [RTX tool](https://github.com/Starofall/RTX) is available at this [Wiki page](https://github.com/Starofall/RTX/wiki/RTX-&-CrowdNav-Getting-Started-Guide). 

### Operational Modes

* Normal mode (`python run.py`) with UI to Debug the application. Runs forever.
* Parallel mode (`python parallel.py n`) to let n processes of SUMO spawn for faster data generation.
  Stops after 10k ticks and reports values.
  
### Further customization

* Runtime variables are in the knobs.json file and will only be used if `kafkaUpdates = True
` is set to false in `Config.py`. Else the tool uses Kafka for value changes.
* To disable the UI in normal mode, change the `sumoUseGUI = True` value in `Config.py` to false.

### Notes

* To let the system stabalize, no message is sent to kafka or CSV in the first 1000 ticks .
