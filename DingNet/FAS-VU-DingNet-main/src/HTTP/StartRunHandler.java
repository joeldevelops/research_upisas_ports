package HTTP;

import Simulation.ScatteredSimulation;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import models.SimulationState;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;

/**
 * This class implements the handler for starting a run in DingNet.
 * @version 1.0
 */
public class StartRunHandler implements HttpHandler {
    /**
     * The simulation state containing information regarding the simulation.
     * @since 1.0
     */
    private final SimulationState simulationState;

    private final static long DEFAULT_SEED = 0L;

    /**
     * An HTTP Response message {@code ALREADY_RUNNING} for when DingNet is already running.
     */
    static private final HTTPResponse ALREADY_RUNNING = new HTTPResponse(
            HttpURLConnection.HTTP_CONFLICT,
            "Simulation is already running.\n"
    );

    /**
     * An HTTP Response message {@code SIMULATION_STARTED} for when DingNet has successfully started.
     */
    static private final HTTPResponse SIMULATION_STARTED = new HTTPResponse(
            HttpURLConnection.HTTP_OK,
            "Simulation started.\n"
    );

    /**
     * Constructs an {@code StartRunHandler} object with the simulation state {@code simulationState}.
     * @param simulationState The state of the simulation to be started.
     * @since 1.0
     */
    public StartRunHandler(SimulationState simulationState) {
        this.simulationState = simulationState;
    }

    private static class InvalidSeedException extends Exception {}

    private static long extractSeed (String queryString) throws InvalidSeedException {
        for (String query : queryString.split("&")) {
            String[] queryParts = query.split("=");

            if (queryParts.length != 2) {
                continue;
            }

            String key = queryParts[0];
            String value = queryParts[1];

            if (key.equals("seed")) {
                try {
                    return Long.parseLong(value);
                } catch (NumberFormatException e) {
                    throw new InvalidSeedException();
                }
            }
        }

        return DEFAULT_SEED;
    }

    /**
     * Starts the simulation of DingNet (if it wasn't running already).
     * The function also resets the SimulationState.
     * @param exchange the exchange containing the request from the
     *      client and used to send the response
     * @exception IOException can occur in {@link HttpExchange#sendResponseHeaders(int, long),
     * {@link OutputStream#write(int)}, {@link OutputStream#flush()} and {@link OutputStream#close()}
     */
    @Override
    public void handle(HttpExchange exchange) throws IOException {
        boolean isRunning = this.simulationState.getIsRunning();
        HTTPResponse response = isRunning ? ALREADY_RUNNING : SIMULATION_STARTED;
        long seed = DEFAULT_SEED;

        String rawQuery = exchange.getRequestURI().getRawQuery();

        if (rawQuery != null) {
            try {
                seed = extractSeed(rawQuery);
            } catch (InvalidSeedException e) {
                new HTTPResponse(
                        HttpURLConnection.HTTP_BAD_REQUEST,
                        "Invalid seed.\n"
                ).send(exchange);
                return;
            }
        }

        if (!isRunning) {
            this.simulationState.setIsRunning(true);
            this.simulationState.setShouldStop(false);
            new ScatteredSimulation(this.simulationState, seed).start();
        }

        response.send(exchange);
    }
}
