package GUI.MapViewer;

import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.util.*;
import java.util.stream.Collectors;

import org.jxmapviewer.JXMapViewer;
import org.jxmapviewer.painter.AbstractPainter;
import org.jxmapviewer.viewer.Waypoint;
import org.jxmapviewer.viewer.WaypointRenderer;

/**
 * Paints waypoints on the JXMapViewer. This is an
 * instance of Painter that only can draw on to JXMapViewers.
 * @param <W> the waypoint type
 * @author rbair
 */
public class MoteWaypointPainter<W extends Waypoint> extends AbstractPainter<JXMapViewer>
{
    private final LinkedHashMap<W, WaypointRenderer<? super W>> waypointRendererMap = new LinkedHashMap<>();

    /**
     * Creates a new instance of WaypointPainter
     */
    public MoteWaypointPainter()
    {
        setAntialiasing(true);
        setCacheable(false);
    }

    public MoteWaypointPainter(List<W> waypoints) {
        super();
        this.setWaypointsRendererMap(
                waypoints.stream().collect(
                        Collectors.toMap(w -> w, w -> new MoteWaypointRenderer())
                )
        );
    }

    public MoteWaypointPainter(LinkedHashMap<W, Integer> waypoints) {
        super();
        this.setWaypointsRendererMap(
                waypoints.keySet().stream().collect(
                        Collectors.toMap(w -> w, w -> new MoteWaypointRenderer(waypoints.get(w)))
                )
        );
    }


    /**
     * Sets the waypoint renderer to use when painting waypoints
     * @param r the new WaypointRenderer to use
     */
    public void setRenderer(WaypointRenderer<W> r, W w) {
        this.waypointRendererMap.put(w, r);
    }

    /**
     * Gets the current set of waypoints to paint
     * @return a typed Set of Waypoints
     */
    public Set<W> getWaypoints()
    {
        return Collections.unmodifiableSet(waypointRendererMap.keySet());
    }

    /**
     * Sets the current set of waypoints to paint
     * @param waypoints the new Set of Waypoints to use
     */
    public void setWaypointsRendererMap(Map<W, WaypointRenderer<? super W>> waypoints)
    {
        this.waypointRendererMap.clear();
        this.waypointRendererMap.putAll(waypoints);
    }

    public void setWaypoints(Set<? extends W> waypoints) {
        this.setWaypointsRendererMap(
                waypoints.stream().collect(
                        Collectors.toMap(w -> w, w -> new MoteWaypointRenderer())
                )
        );
    }

    @Override
    protected void doPaint(Graphics2D g, JXMapViewer map, int width, int height)
    {
        if (waypointRendererMap == null)
        {
            return;
        }

        Rectangle viewportBounds = map.getViewportBounds();

        g.translate(-viewportBounds.getX(), -viewportBounds.getY());

        for (W w : waypointRendererMap.keySet()) {
            waypointRendererMap.get(w).paintWaypoint(g, map, w);
        }

        g.translate(viewportBounds.getX(), viewportBounds.getY());

    }

}
