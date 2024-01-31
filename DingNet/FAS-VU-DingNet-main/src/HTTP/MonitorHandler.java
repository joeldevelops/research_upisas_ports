package HTTP;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import mappers.SimulationStateMapper;
import models.SimulationState;

import java.io.IOException;
import java.net.HttpURLConnection;

/**
 * This class implements the handler for an HTTP request to the monitor endpoint of DingNet.
 * @version 1.0
 */
public class MonitorHandler implements HttpHandler {

    /**
     * The current state of the simulation to be monitored.
     * @since 1.0
     */
    private final SimulationState simulationState;

    /**
     * An {@code ObjectMapper} instance to map the simulation state to a JSON string.
     * @since 1.0
     */
    private final ObjectMapper objectMapper;

    /**
     * Constructs a {@code MonitorHandler} object with the simulation state {@code state}.
     * @param simulationState The state of the simulation to be monitored by this monitor handler.
     * @since 1.0
     */
    public MonitorHandler(SimulationState simulationState) {
        this.simulationState = simulationState;
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Sends a response with the HTTP Status Code {@code 200 OK} and the monitored values of DingNet as JSON
     * to the HTTP {@code exchange}. Overrides the method {@link HttpHandler#handle(HttpExchange)}.
     * @param exchange The HTTP exchange with the monitor endpoint.
     * @exception IOException can occur in {@link HTTPResponse#send(HttpExchange)}
     * @since 1.0
     */
    @Override
    public void handle(HttpExchange exchange) throws IOException {
        String data = this.objectMapper.writeValueAsString(
                SimulationStateMapper.mapSimulationStateToMonitorModel(this.simulationState)
        );
        HTTPResponse response = new HTTPResponse(HttpURLConnection.HTTP_OK, data);

        exchange.getResponseHeaders().add("Content-Type", "application/json");

        response.send(exchange);
    }
}
