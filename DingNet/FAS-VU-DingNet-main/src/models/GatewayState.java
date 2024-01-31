package models;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

/**
 * The Class responsible for storing the values of a gateway that is monitored.
 */
@Data
@Builder
@AllArgsConstructor
public class GatewayState {
    /**
     * The gateway identifier.
     */
    private Long EUI;

    /**
     * The x-coordinate of the gateway.
     */
    private Integer XPos;

    /**
     * The y-coordinate of the gateway.
     */
    private Integer YPos;

    /**
     * The spreading factor of the gateway.
     */
    private Integer SF;

    /**
     * The transmission power of the gateway.
     */
    private Integer transmissionPower;
}
