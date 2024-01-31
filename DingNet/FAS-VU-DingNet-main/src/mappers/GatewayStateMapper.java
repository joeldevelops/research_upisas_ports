package mappers;

import IotDomain.Gateway;
import models.GatewayState;

import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

public class GatewayStateMapper {
    public static List<GatewayState> mapGatewayListToGatewayStateList(LinkedList<Gateway> gateways) {
        return gateways.stream()
                .map(GatewayStateMapper::mapGatewayToGatewayState)
                .collect(Collectors.toList());
    }

    public static GatewayState mapGatewayToGatewayState(Gateway gateway) {
        return GatewayState.builder()
                .EUI(gateway.getEUI())
                .XPos(gateway.getXPos())
                .YPos(gateway.getYPos())
                .SF(gateway.getSF())
                .transmissionPower(gateway.getTransmissionPower())
                .build();
    }
}
