bsn=$PWD/src/sa-bsn
exec_time=0

source $STARTUPDIR/generate_container_user
source /opt/ros/melodic/setup.bash
source /home/kasm-default-profile/Desktop/BSN/devel/setup.bash

if [[ "$#" -gt 1 ]]; then
    echo "Too many arguments were passed!"
    exit 1
fi

if [[ "$#" -eq 0 ]]; then
    exec_time=300
else
    exec_time=$1
fi

if [[ -n ${exec_time//[0-9]/} ]]; then
    echo "The execution time is not an integer!"
    exit 1
fi

################# HTTP ENDPOINT ##############
python3 src/sa-bsn/target_system/components/component/listener.py & sleep 1s

roscore & sleep 5s

################# KNOWLEDGE REPOSITORY #################
roslaunch --pid=/var/tmp/data_access.pid ${bsn}/configurations/knowledge_repository/data_access.launch & sleep 1s

################# MANAGER SYSTEM #################
roslaunch --pid=/var/tmp/strategy_manager.pid ${bsn}/configurations/system_manager/strategy_manager.launch & sleep 7s

roslaunch --pid=/var/tmp/strategy_enactor.pid ${bsn}/configurations/system_manager/strategy_enactor.launch & sleep 1s

################# LOGGING INFRASTRUCTURE #################
roslaunch --pid=/var/tmp/logger.pid ${bsn}/configurations/logging_infrastructure/logger.launch & sleep 1s

################# APPLICATION #################
roslaunch --pid=/var/tmp/probe.pid ${bsn}/configurations/target_system/probe.launch & sleep 1s
roslaunch --pid=/var/tmp/effector.pid ${bsn}/configurations/target_system/effector.launch & sleep 1s

roslaunch --pid=/var/tmp/g4t1.pid ${bsn}/configurations/target_system/g4t1.launch &
roslaunch --pid=/var/tmp/patient.pid ${bsn}/configurations/environment/patient.launch & sleep 5s

roslaunch --pid=/var/tmp/g3t1_1.pid ${bsn}/configurations/target_system/g3t1_1.launch & sleep 2s
roslaunch --pid=/var/tmp/g3t1_2.pid ${bsn}/configurations/target_system/g3t1_2.launch & sleep 2s
roslaunch --pid=/var/tmp/g3t1_3.pid ${bsn}/configurations/target_system/g3t1_3.launch & sleep 2s
roslaunch --pid=/var/tmp/g3t1_4.pid ${bsn}/configurations/target_system/g3t1_4.launch & sleep 2s
roslaunch --pid=/var/tmp/g3t1_5.pid ${bsn}/configurations/target_system/g3t1_5.launch & sleep 2s
roslaunch --pid=/var/tmp/g3t1_6.pid ${bsn}/configurations/target_system/g3t1_6.launch & sleep 2s

################# SIMULATION #################
roslaunch --pid=/var/tmp/injector.pid ${bsn}/configurations/simulation/injector.launch & sleep ${exec_time}s

kill $(cat /var/tmp/data_access.pid && rm /var/tmp/data_access.pid) & sleep 1s
kill $(cat /var/tmp/strategy_enactor.pid && rm /var/tmp/strategy_enactor.pid) & sleep 1s
kill $(cat /var/tmp/logger.pid && rm /var/tmp/logger.pid) & sleep 1s
kill $(cat /var/tmp/probe.pid && rm /var/tmp/probe.pid) & sleep 1s
kill $(cat /var/tmp/effector.pid && rm /var/tmp/effector.pid) & sleep 1s
kill $(cat /var/tmp/g4t1.pid && rm /var/tmp/g4t1.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_1.pid && rm /var/tmp/g3t1_1.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_2.pid && rm /var/tmp/g3t1_2.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_3.pid && rm /var/tmp/g3t1_3.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_4.pid && rm /var/tmp/g3t1_4.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_5.pid && rm /var/tmp/g3t1_5.pid) & sleep 1s
kill $(cat /var/tmp/g3t1_6.pid && rm /var/tmp/g3t1_6.pid) & sleep 1s
kill $(cat /var/tmp/patient.pid && rm /var/tmp/patient.pid) & sleep 1s
kill $(cat /var/tmp/injector.pid && rm /var/tmp/injector.pid) & sleep 1s
kill $(cat /var/tmp/strategy_manager.pid && rm /var/tmp/strategy_manager.pid) & sleep 1s

kill $(pgrep roscore)
