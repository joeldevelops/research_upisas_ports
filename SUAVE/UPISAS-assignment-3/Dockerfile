FROM python:3.12

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

env DOCKER_HOST="unix://var/run/docker.sock"

CMD ["python", "run.py"]