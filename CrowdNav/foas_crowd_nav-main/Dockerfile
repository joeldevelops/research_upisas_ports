# Get crowdnav image from Dockerhub as base image
FROM starofall/crowdnav:latest
# Add setup file and execute the setup steps from the file 
ADD ./setup.py /app/setup.py
RUN python /app/setup.py install
# Add sources
ADD ./ /app/
# Set the working directory
WORKDIR /app
# Expose port 3000 for external access
EXPOSE 3000
# Make the run.sh script executable
RUN chmod +x ./run.sh
# Setup the server and start simulation by running the run.sh file when the container starts
CMD ["bash","./run.sh"]

