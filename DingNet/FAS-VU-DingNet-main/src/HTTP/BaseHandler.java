package HTTP;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;

/**
 * This class is a base class for a handler of an HTTP exchange.
 * @version 1.0
 */
public class BaseHandler implements HttpHandler {

    /**
     * Sends a response with the HTTP Status Code {@code 200 OK} and the body "OK"
     * to the HTTP {@code exchange}. Overrides method {@link HttpHandler#handle(HttpExchange)}
     * @param exchange The HTTP exchange to be handled.
     * @exception IOException can occur in {@link HttpExchange#sendResponseHeaders(int, long),
     * {@link OutputStream#write(int)}, {@link OutputStream#flush()} and {@link OutputStream#close()}
     * @since 1.0
     */
    @Override
    public void handle(HttpExchange exchange) throws IOException {
        byte[] data = "OK\n".getBytes();
        int contentLength = data.length;

        exchange.sendResponseHeaders(HttpURLConnection.HTTP_OK, contentLength);

        OutputStream os = exchange.getResponseBody();
        os.write(data);
        os.flush();
        os.close();

        exchange.close();
    }
}
