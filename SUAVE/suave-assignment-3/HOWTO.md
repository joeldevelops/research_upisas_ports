# How to run (and develop) the system?

## Docker Installation

> [!WARNING]  
> For now, our version of SUAVE can be deployed or tested _with either Docker installation or local installation_. 
> However, it is very much recommended and preferred to be installed and run with a local SUAVE installation.

1. Pull the Docker image
    ```bash
    docker pull ghcr.io/caesarw/suave-custom:main
    ```

2. Start the docker container
    ```bash
    docker run -it -p 3000:3000 ghcr.io/caesarw/suave-custom:main
    ```

After starting the Docker container, the headless runner script will be automatically running to start all components of 
the system, including the HTTP server.

> [!NOTE]  
> However, if you wish to use the Docker image for exploration, debugging or further development, you can also override
> the default Docker entry point and land on a shell, by:
> ```bash
> docker run -it -p 3000:3000 --entrypoint /bin/bash ghcr.io/caesarw/suave-custom:main
> ```
> The above command will land you onto a `bash` shell. 

## Run without GUI (headless) manually
If you decide to run it manually, it is necessary to maintain multiple terminal session. It is recommended to use tmux (on Linux).

#### Start ArduSub

Start a new terminal session and run:
```Bash
source ~/suave_ws/install/setup.bash
sim_vehicle.py -v ArduSub -L RATBeach --console --map false
```

#### Start the simulation

Start a new terminal session and run:
```Bash
source ~/suave_ws/install/setup.bash
ros2 launch suave simulation.launch.py x:=-17.0 y:=2.0 gui:=false
```

#### Start SUAVE's nodes

Start a new terminal session and run:
```Bash
source ~/suave_ws/install/setup.bash
ros2 launch suave_missions mission.launch.py
```

#### Start our HTTP server
Start a new terminal session and run:
```Bash
source ~/suave_ws/install/setup.bash
python ~/suave_ws/src/suave/suave_externalcontrol/suave_externalcontrol/http_server.py
```
Now you will have a fully working setup ready to test. To continue the test, configure UPISAS to use `localhost:3000`. 