package GUI.MapViewer;

import java.awt.*;
import java.awt.geom.AffineTransform;
import java.awt.geom.Point2D;
import java.awt.image.AffineTransformOp;
import java.awt.image.BufferedImage;

import javax.imageio.ImageIO;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.jxmapviewer.JXMapViewer;
import org.jxmapviewer.viewer.DefaultWaypointRenderer;
import org.jxmapviewer.viewer.Waypoint;
import org.jxmapviewer.viewer.WaypointRenderer;

/**
 * This is a standard waypoint renderer.
 * @author joshy
 */
public class MoteWaypointRenderer implements WaypointRenderer<Waypoint>
{
    private static final Log log = LogFactory.getLog(GatewayWaypointRenderer.class);

    private BufferedImage img = null;

    public static final int SPECIAL_MOTE_OFFSET = 1024;


    /**
     * Uses a default waypoint image
     */
    public MoteWaypointRenderer() {
        this(null);
    }

    private String toResourcePath(Integer digit) {
        String base = "/GUI/MapViewer/mote";
        String extension = ".png";

        if (digit != null && digit > SPECIAL_MOTE_OFFSET) {
            return base + ("-special-" + (digit - SPECIAL_MOTE_OFFSET)) + extension;
        }

        return base + (digit != null ? ("-" + digit) : "_after_edit") + extension;
    }

    /**
     * Uses the digit 7-12 (representing spreading factor) to render on the mote
     */
    public MoteWaypointRenderer(Integer digit) {
        boolean isSpecial = digit != null && digit > SPECIAL_MOTE_OFFSET;
        String resourcePath = toResourcePath(digit);

        try
        {
            img = ImageIO.read(DefaultWaypointRenderer.class.getResource(resourcePath));
            int w = img.getWidth();
            int h = img.getHeight();
            BufferedImage after = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
            AffineTransform at = new AffineTransform();
            at.scale(isSpecial ? 0.3 : 0.2, isSpecial ? 0.3 : 0.2);
            AffineTransformOp scaleOp =
                    new AffineTransformOp(at, AffineTransformOp.TYPE_BILINEAR);
            img = scaleOp.filter(img, after);
        }
        catch (Exception ex)
        {

        }
    }

    @Override
    public void paintWaypoint(Graphics2D g, JXMapViewer map, Waypoint w)
    {
        if (img == null)
            return;

        Point2D point = map.getTileFactory().geoToPixel(w.getPosition(), map.getZoom());

        int x = (int)point.getX() -img.getWidth() *1/10;
        int y = (int)point.getY() -img.getHeight()*1/10;

        g.drawImage(img, x, y, null);
    }
}
