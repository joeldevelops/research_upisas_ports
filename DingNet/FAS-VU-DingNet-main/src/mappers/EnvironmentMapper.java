package mappers;

import IotDomain.Environment;
import models.MonitorModel;

public class EnvironmentMapper {
    public static MonitorModel mapEnvironmentToMonitorModel(Environment environment) {
        if (environment == null)
            return new MonitorModel();

        return MonitorModel.builder()
                .gatewayStates(GatewayStateMapper.mapGatewayListToGatewayStateList(environment.getGateways()))
                .moteStates(MoteStateMapper.mapMoteListToMoteStateList(environment.getMotes()))
                .build();
    }
}
