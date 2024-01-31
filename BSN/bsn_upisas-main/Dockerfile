FROM egalberts/bsn:latest
RUN sudo apt update && sudo apt upgrade -y
RUN sudo apt install -y python3-pip python3-yaml ros-melodic-desktop-full git xrdp gnome-terminal
RUN sudo service xrdp start
WORKDIR /home/kasm-user/Desktop/
RUN git clone https://hfvw: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@github.com/hfvw/bsn.git
WORKDIR /home/kasm-user/Desktop/bsn/
RUN pip3 install -r requirements.txt

EXPOSE 3000

ENTRYPOINT ["bash", "-c"]
CMD ["bash run.sh 999"]
