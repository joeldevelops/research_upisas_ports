# Team: 2_4_Emergent Web Server

# Instructions for running EWS independently

Build and run two docker containers in the background (named emergent_web_server and fastapi_server) using docker compose.
```
cd Docker
docker compose up --build -d
```
Test if ews is running properly by executing its bash terminal, starting up the server and trying out different commands.
```
docker exec -it emergent_web_server bash
dana -sp ../repository InteractiveEmergentSys.o
sys> get_all_configs
```
To run one of the client scripts for ews, execute the following commands in a separate terminal. This step is necessary for generating perception data for the `monitor` endpoint.
```
docker exec -it emergent_web_server bash
cd ../ws_clients
dana ClientTextPattern.o
```
Test if fastapi server is running properly by visiting `http://localhost:8000`. You should receive the response `{"message":"Hello World"}`. The fastapi code can be found in the `http_server` folder.

For Swagger/OpenAPI docs, visit `http://localhost:8000/docs`. You can try out all the endpoints here.

# Instructions for testing EWS via UPISAS

Only the docker images need to be built for UPISAS to create docker containers from them while testing endpoints.
```
cd Docker
docker compose build
```
For MacOS, we have provided some additional comments in the file `Docker/docker-compose.yml` in case there are issues with building the ews docker image from the code in this repository.
