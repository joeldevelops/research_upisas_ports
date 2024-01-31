package HTTP;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import models.AdaptationOptionsDTO;

import java.io.IOException;
import java.net.HttpURLConnection;

/**
 * This class implements the handler for an HTTP request for the JSON schema
 * of the response to the adaption options endpoint.
 * @version 1.0
 */
public class AdaptationOptionsSchemaHandler implements HttpHandler {

    /**
     * Sends a response with the HTTP Status Code {@code 200 OK} and the JSON schema of the adaption options of DingNet
     * to the HTTP {@code exchange}. Overrides method {@link HttpHandler#handle(HttpExchange)}
     * @param exchange The HTTP exchange with the adaptation options schema endpoint.
     * @exception IOException can occur in {@link HttpExchange#sendResponseHeaders(int, long)
     * @since 1.0
     */
    @Override
    public void handle(HttpExchange exchange) throws IOException {
        String data = Schema.toJsonSchema(AdaptationOptionsDTO.class);
        HTTPResponse response = new HTTPResponse (HttpURLConnection.HTTP_OK, data);

        exchange.getResponseHeaders().add("Content-Type", "application/json");

        response.send(exchange);
    }
}
