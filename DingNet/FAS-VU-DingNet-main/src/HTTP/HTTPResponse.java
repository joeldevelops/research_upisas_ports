package HTTP;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.io.IOException;
import java.io.OutputStream;

/**
 * This class implements a container class for a HTTP response.
 * @version 1.0
 */
@Data
@AllArgsConstructor
public class HTTPResponse {

    /**
     * The HTTP Status code to be returned in the HTTP response.
     * @since 1.0
     */
    int code;

    /**
     * The body of the HTTP response.
     * @since 1.0
     */
    String body;

    /**
     * Sends the HTTP response represented by this object to the HTTP {@code exchange}.
     * @param exchange The HTTP exchange to send the response to.
     * @exception IOException can occur in {@link HttpExchange#sendResponseHeaders(int, long),
     * {@link OutputStream#write(int)}, {@link OutputStream#flush()} and {@link OutputStream#close()}
     * @since 1.0
     */
    public void send(HttpExchange exchange) throws IOException {
        exchange.sendResponseHeaders(this.code, this.body.getBytes().length);

        OutputStream os = exchange.getResponseBody();
        os.write(this.body.getBytes());
        os.flush();
        os.close();

        exchange.close();
    }
}
