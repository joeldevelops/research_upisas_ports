package Simulation;

import GUI.MapViewer.BorderPainter;
import GUI.MapViewer.GatewayWaypointPainter;
import GUI.MapViewer.MoteWaypointPainter;
import IotDomain.*;
import SelfAdaptation.Instrumentation.MoteProbe;
import models.SimulationState;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.axis.NumberTickUnit;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jxmapviewer.JXMapViewer;
import org.jxmapviewer.OSMTileFactoryInfo;
import org.jxmapviewer.painter.CompoundPainter;
import org.jxmapviewer.painter.Painter;
import org.jxmapviewer.viewer.*;

import javax.swing.*;
import javax.swing.border.CompoundBorder;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.time.LocalTime;
import java.util.List;
import java.util.*;
import java.util.stream.Collectors;

import static GUI.MapViewer.MoteWaypointRenderer.SPECIAL_MOTE_OFFSET;

/**
 * This class provides the data and functionality of the main simulation.
 * @version 1.0
 */
public class ScatteredSimulation extends Thread {

    private static final MoteProbe moteProbe = new MoteProbe();
    private final long randomSeed;

    /**
     * The current environment of the simulation.
     * @since 1.0
     */
    SimulationState simulationState;

    /**
     * Constructs a {@code ScatteredSimulation} object with the simulation state {@code simulationState}.
     * @param simulationState The state of the simulation to be started.
     * @since 1.0
     */
    public ScatteredSimulation(SimulationState simulationState, long randomSeed) {
        this.simulationState = simulationState;
        this.randomSeed = randomSeed;
    }

    public static Environment createEnvironment(long randomSeed) {
        Random random = new Random(randomSeed);
        final int mapSize = 2000;
        GeoPosition mapZero = new GeoPosition(50.853718, 4.673155);

        /*
         * Prepare simulation environment.
         */
        Characteristic[][] map = new Characteristic[mapSize][mapSize];
        Arrays.stream(map).forEach(row -> Arrays.fill(row, Characteristic.Forest));

        Environment environment = new Environment(map, mapZero, new LinkedHashSet<>());

        /*
         *  Create main mote and gateways, M represent our main mote, numbers represent gateways
         *  +-------------+
         *  |  1       2  |
         *  |      M      |
         *  |  3       4  |
         *  +-------------+
         */
        final int distanceFromBorder = 100;

        // Gateway 1
        new Gateway(random.nextLong(), distanceFromBorder, environment.getMaxYpos() - distanceFromBorder, environment, 14, 12);

        // Gateway 2
        new Gateway(random.nextLong(), environment.getMaxXpos() - distanceFromBorder, environment.getMaxYpos() - distanceFromBorder, environment, 14, 12);

        // Gateway 3
        new Gateway(random.nextLong(), distanceFromBorder, distanceFromBorder, environment, 14, 12);

        // Gateway 4
        new Gateway(random.nextLong(), environment.getMaxXpos() - distanceFromBorder, distanceFromBorder, environment, 14, 12);

        // Main mote
        Mote mainMote = new Mote(random.nextLong(), environment.getMaxXpos() / 2, environment.getMaxYpos() / 2, environment, 14,11, new LinkedList<>(),0, new LinkedList<>(),10,0.5);


        final int numMotes = 20;

        /*
         * Add 'numMotes' motes randomly scattered on the map
         */
        for (int j = 0; j < numMotes; j++) {
            new Mote(random.nextLong(),
                    random.nextInt(environment.getMaxXpos()),
                    random.nextInt(environment.getMaxYpos()),
                    environment, 14, random.nextInt(6) + 7, new LinkedList<>(), 0, new LinkedList<>(), 10, 0.5);
        }

        Map<Integer, Integer> spreadingFactorDistribution = new HashMap<>();
        for (Mote mote : environment.getMotes()) {
            if (mote == mainMote) {
                continue;
            }

            spreadingFactorDistribution.put(moteProbe.getSpreadingFactor(mote), spreadingFactorDistribution.getOrDefault(moteProbe.getSpreadingFactor(mote), 0) + 1);
        }

        // Least common spreading factor should be the best to get the lowest packet loss
        System.out.println("Least common spreading factor: " + spreadingFactorDistribution.entrySet().stream().min(Comparator.comparingInt(Map.Entry::getValue)).get().getKey());
        System.out.println(spreadingFactorDistribution);

        return environment;
    }

    /**
     * Starts a DingNet simulation with three motes and four gateways. Two motes are moved along different paths.
     * The simulation state is updated regularly.
     * @exception InterruptedException can occur in {@link Thread#sleep(long)}
     * @since 1.0
     */
    public void runSimulation(boolean visualizeResults) throws InterruptedException {
        /*
        Set to enable or disable adaptation of node 0 (D1).
         */
        Boolean adaption = false;

        Environment environment = createEnvironment(this.randomSeed);
        JFrame frame = createMap(environment);

        /*
         Get the motes.
         */
        Mote mainMote = environment.getMotes().get(0);
        this.simulationState.setEnvironment(environment);

        /*
         Actual simulation
         */
        int mainMoteIterationsSincePacket = 0;
        Random random = new Random(this.randomSeed);

        System.out.printf("Simulation started with seed %d%n", this.randomSeed);

        for(int simulationIteration = 0; !simulationState.getShouldStop(); simulationIteration++) {
            if(mainMoteIterationsSincePacket == 9) {
                mainMote.sendToGateWay(new Byte[0], new HashMap<>());
                mainMote.setHighestReceivedSignal(moteProbe.getHighestReceivedSignal(mainMote));
                mainMote.setShortestDistanceToGateway(moteProbe.getShortestDistanceToGateway(mainMote));
                mainMote.setPacketLoss(mainMote.calculatePacketLoss(environment.getNumberOfRuns() - 1));
                mainMoteIterationsSincePacket = 0;
            } else {
                mainMoteIterationsSincePacket++;
            }

            for (Mote mote : environment.getMotes()) {
                if (mote == mainMote)
                    continue;

                // Motes send a packet at random intervals, on average once every 10 iterations
                if (random.nextInt(10) == 0) {
                    mote.sendToGateWay(new Byte[0], new HashMap<>());
                }
            }

            // Render map updates every 100 iterations
            if (simulationIteration % 100 == 0) {
                updateMap(frame, environment, mainMote);
                System.out.println(simulationIteration);
            }

            environment.tick(10000);
        }

        simulationState.setIsRunning(false);

        frame.dispose();
    }

    private static void updateMap(JFrame frame, Environment environment, Mote mainMote) {
        JXMapViewer mapViewer = (JXMapViewer) frame.getContentPane().getComponent(0);
        JPanel statusBar = (JPanel) frame.getContentPane().getComponent(1);

        JLabel label = (JLabel) statusBar.getComponent(0);
        label.setText(String.format(
                "Packets sent %-20d Packets lost: %-20d Packet loss: %.3f",
                mainMote.getNumberOfSentPackets(),
                Math.round(mainMote.calculatePacketLoss(environment.getNumberOfRuns() - 1) * mainMote.getNumberOfSentPackets()),
                mainMote.calculatePacketLoss(environment.getNumberOfRuns() - 1)
        ));

        List<BorderPainter> borderPainters = environment
                .getMotes()
                .stream()
                .map(Mote::getPath)
                .map(BorderPainter::new)
                .collect(Collectors.toList());

        Set<Waypoint> gatewayWaypoints = environment
                .getGateways()
                .stream()
                .map(gateway -> new DefaultWaypoint(
                        environment.toLatitude(gateway.getYPos()),
                        environment.toLongitude(gateway.getXPos())
                ))
                .collect(Collectors.toSet());

        LinkedHashMap<Waypoint, Integer> moteWaypoints = environment
                .getMotes()
                .stream()
                .filter(mote -> mote != mainMote)
                .collect(Collectors.toMap(
                        mote -> new DefaultWaypoint(
                                environment.toLatitude(mote.getYPos()),
                                environment.toLongitude(mote.getXPos())
                        ),
                        moteProbe::getSpreadingFactor,
                        (a, b) -> { throw new RuntimeException("Duplicate motes"); },
                        LinkedHashMap::new
                ));

        GatewayWaypointPainter<Waypoint> gatewayPainter = new GatewayWaypointPainter<>(gatewayWaypoints);
        MoteWaypointPainter<Waypoint> motePainter = new MoteWaypointPainter<>(moteWaypoints);

        MoteWaypointPainter<Waypoint> specialWaypointPainter = new MoteWaypointPainter<>(
                new LinkedHashMap<>(Collections.singletonMap(new DefaultWaypoint(
                    environment.toLatitude(mainMote.getYPos()),
                    environment.toLongitude(mainMote.getXPos())
                ),
                SPECIAL_MOTE_OFFSET + moteProbe.getSpreadingFactor(mainMote)
            )));

        List<Painter<JXMapViewer>> allPainters = new ArrayList<>(borderPainters);
        allPainters.add(gatewayPainter);
        allPainters.add(motePainter);
        allPainters.add(specialWaypointPainter);

        mapViewer.setOverlayPainter(new CompoundPainter<>(allPainters));
        mapViewer.updateUI();
    }

    private static JFrame createMap(Environment environment) {
        JXMapViewer mapViewer = new JXMapViewer();

        // Create a TileFactoryInfo for OpenStreetMap
        TileFactoryInfo info = new OSMTileFactoryInfo();
        DefaultTileFactory tileFactory = new DefaultTileFactory(info);
        mapViewer.setTileFactory(tileFactory);

        // Use 8 threads in parallel to load the tiles
        tileFactory.setThreadPoolSize(8);

        mapViewer.setZoom(4);
        mapViewer.setAddressLocation(environment.getMapCenter());
        mapViewer.setPreferredSize(new Dimension(800, 600));

        JPanel statusBar = new JPanel(new FlowLayout(FlowLayout.LEFT));
        statusBar.setBorder(new CompoundBorder(new LineBorder(Color.DARK_GRAY), new EmptyBorder(4, 4, 4, 4)));
        statusBar.add(new JLabel(String.format("Packets sent %-10d Packets lost: %-10d Packet loss: %.3f", 0, 0, 0F)));

        // Display the viewer in a JFrame
        JFrame frame = new JFrame("Dingnet");
        frame.setLayout(new BorderLayout());
        frame.getContentPane().add(mapViewer);
        frame.getContentPane().add(statusBar, BorderLayout.SOUTH);
        frame.setSize(1200, 900);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);

        updateMap(frame, environment, environment.getMotes().isEmpty() ? null : environment.getMotes().get(0));

        return frame;
    }

    private static void showCharts(Environment environment) {
        /*
        * Data collection mote 0
        */
        LinkedList<LinkedList<LoraTransmission>> transmissionsMote0 = new LinkedList<>();
        int transmittedPacketsMote0 = 0;
        int lostPacketsMote0 = 0;
        for(Gateway gateway : environment.getGateways()){
            transmissionsMote0.add(new LinkedList<>());
            for(LoraTransmission transmission :gateway.getAllReceivedTransmissions(gateway.getEnvironment().getNumberOfRuns()-1).keySet()){
                if(transmission.getSender() == environment.getMotes().get(0)) {
                    transmittedPacketsMote0++;
                    if (!gateway.getAllReceivedTransmissions(gateway.getEnvironment().getNumberOfRuns()-1).get(transmission))
                        transmissionsMote0.getLast().add(transmission);
                    else {
                        transmissionsMote0.getLast().add(new LoraTransmission(transmission.getSender(),
                                transmission.getReceiver(), -10, transmission.getBandwidth(),
                                transmission.getSpreadingFactor(), transmission.getContent()));
                        lostPacketsMote0++;
                    }
                }
            }
        }

        /*
         * Creating charts
         */
        XYSeriesCollection dataMote0 = new XYSeriesCollection();
        for(LinkedList<LoraTransmission> list : transmissionsMote0){
            XYSeries series = new XYSeries(list.get(0).getReceiver().toString());
            Integer i = 0;
            for (LoraTransmission transmission: list){
                series.add(i,(Number)transmission.getTransmissionPower());
                i = i +10;
            }
            dataMote0.addSeries(series);
        }

        JFreeChart receivedPowerChartMote0 = ChartFactory.createScatterPlot(
                null, // chart title
                "Distance travelled in meter", // x axis label
                "Received signal strength in dB", // y axis label
                dataMote0, // data
                PlotOrientation.VERTICAL,
                true, // include legend
                true, // tooltips
                false // urls
        );
        XYPlot xyPlotreceivedPowerMote0 = (XYPlot) receivedPowerChartMote0.getPlot();
        xyPlotreceivedPowerMote0.setDomainCrosshairVisible(true);
        xyPlotreceivedPowerMote0.setRangeCrosshairVisible(true);
        NumberAxis domainreceivedPowerMote0 = (NumberAxis) xyPlotreceivedPowerMote0.getDomainAxis();
        domainreceivedPowerMote0.setRange(0.0, 2700.0);
        domainreceivedPowerMote0.setTickUnit(new NumberTickUnit(200));
        domainreceivedPowerMote0.setVerticalTickLabels(true);
        NumberAxis rangereceivedPowerMote0 = (NumberAxis) xyPlotreceivedPowerMote0.getRangeAxis();
        rangereceivedPowerMote0.setRange(-85, 0.0);
        rangereceivedPowerMote0.setTickUnit(new NumberTickUnit(4));

        JFrame frame1 = new JFrame("received signals");
        ChartPanel HighestSignalChartpanel = new ChartPanel(receivedPowerChartMote0);
        HighestSignalChartpanel.setPreferredSize(new Dimension(1000, 500));
        frame1.getContentPane().add(HighestSignalChartpanel, BorderLayout.NORTH);
        frame1.pack();
        frame1.setVisible(true);
    }

    /**
     * Runs the simulation and sets the {@code isRunning} flag of the simulation state to {@code false} again.
     * @exception RuntimeException can occur in {@link ScatteredSimulation#runSimulation(boolean)}
     * @since 1.0
     */
    public void run() {
        try {
            this.runSimulation(true);
            this.simulationState.setIsRunning(false);
        } catch (InterruptedException e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    /*
    The naïve adaptation for our paper
     */
    private static LinkedList<Double> algorithmBuffer = new LinkedList<>();
    private static LoraTransmission naiveAdaptionAlgorithm(Mote mote){
        LinkedList<LoraTransmission> lastTransmissions = new LinkedList<>();
        for(Gateway gateway :mote.getEnvironment().getGateways()){
            Boolean placed = false;
            for(int i = gateway.getReceivedTransmissions(gateway.getEnvironment().getNumberOfRuns()-1).size()-1; i>=0 && !placed; i--) {
                if(gateway.getReceivedTransmissions(gateway.getEnvironment().getNumberOfRuns()-1).get(i).getSender() == mote) {
                    lastTransmissions.add(gateway.getReceivedTransmissions(gateway.getEnvironment().getNumberOfRuns()-1).get(i));
                    placed = true;
                }
            }
        }
        LoraTransmission bestTransmission = lastTransmissions.getFirst();
        for (LoraTransmission transmission : lastTransmissions){
            if(transmission.getTransmissionPower() > bestTransmission.getTransmissionPower())
                bestTransmission = transmission;
        }
        algorithmBuffer.add(bestTransmission.getTransmissionPower());
        if(algorithmBuffer.size() ==5){
            double average = 0;
            for (Double power : algorithmBuffer){
                average+= power;
            }
            average = average /5;
            if(average > -42) {
                if (mote.getTransmissionPower() > -3)
                    mote.setTransmissionPower(mote.getTransmissionPower() - 1);
            }
            if(average < -48){
                if(mote.getTransmissionPower() < 14)
                    mote.setTransmissionPower(mote.getTransmissionPower() +1);
            }
            algorithmBuffer = new LinkedList<>();
        }
        return bestTransmission;
    }

    /**
     * A function that moves a mote to a geoposition 1 step and returns if the note has moved.
     * @param position
     * @param mote
     * @param mapzero
     * @return If the node has moved
     */
    private static Boolean moveMote(GeoPosition position, Mote mote, GeoPosition mapzero){
        Integer xPos = toMapXCoordinate(position, mapzero);
        Integer yPos = toMapYCoordinate(position, mapzero);
        if(Integer.signum(xPos - mote.getXPos()) != 0 || Integer.signum(yPos - mote.getYPos()) != 0){
            if(Math.abs(mote.getXPos() - xPos) >= Math.abs(mote.getYPos() - yPos)){
                mote.setXPos(mote.getXPos() + Integer.signum(xPos - mote.getXPos()));
            }  else {
                mote.setYPos(mote.getYPos() + Integer.signum(yPos - mote.getYPos()));
            }
            return true;
        }
        return false;
    }

    private static Integer toMapXCoordinate(GeoPosition geoPosition, GeoPosition mapzero){
        return (int)Math.round(1000* Environment.distance(mapzero.getLatitude(),mapzero.getLongitude(),mapzero.getLatitude(), geoPosition.getLongitude()));
    }

    private static Integer toMapYCoordinate(GeoPosition geoPosition, GeoPosition mapzero){
        return (int)Math.round(1000* Environment.distance(mapzero.getLatitude(),mapzero.getLongitude(),geoPosition.getLatitude(), mapzero.getLongitude()));
    }

    public static void main(String[] args) throws InterruptedException {
        new ScatteredSimulation(new SimulationState(), LocalTime.now().toNanoOfDay()).runSimulation(true);
    }
}
