package mappers;

import models.MonitorModel;
import models.SimulationState;

public class SimulationStateMapper {
    public static MonitorModel mapSimulationStateToMonitorModel(SimulationState simulationState) {
        MonitorModel monitorModel = EnvironmentMapper.mapEnvironmentToMonitorModel(simulationState.getEnvironment());

        monitorModel.setIsRunning(simulationState.getIsRunning());

        return monitorModel;
    }
}
