package mappers;

import IotDomain.Mote;
import SelfAdaptation.Instrumentation.MoteProbe;
import models.MoteState;

import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;

public class MoteStateMapper {
    public static List<MoteState> mapMoteListToMoteStateList(LinkedList<Mote> motes) {
        return motes.stream()
                .map(MoteStateMapper::mapMoteToMoteState)
                .collect(Collectors.toList());
    }

    public static MoteState mapMoteToMoteState(Mote mote) {
        return MoteState.builder()
                .EUI(mote.getEUI())
                .transmissionPower(mote.getTransmissionPower())
                .shortestDistanceToGateway(mote.getShortestDistanceToGateway())
                .highestReceivedSignal(mote.getHighestReceivedSignal())
                .SF(mote.getSF())
                .XPos(mote.getXPos())
                .YPos(mote.getYPos())
                .energyLevel(mote.getEnergyLevel())
                .movementSpeed(mote.getMovementSpeed())
                .samplingRate(mote.getSamplingRate())
                .sensors(mote.getSensors())
                .startOffSet(mote.getStartOffset())
                .packetLoss(mote.getPacketLoss())
                .packetsSent(mote.getNumberOfSentPackets())
                .packetsLost(mote.getNumberOfLostPackets())
                .build();
    }
}
