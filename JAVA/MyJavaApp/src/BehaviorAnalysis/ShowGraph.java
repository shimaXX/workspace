package BehaviorAnalysis;

import java.awt.Color;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;
//import org.jfree.ui.Spacer;

public class ShowGraph extends ApplicationFrame{

	private static final long serialVersionUID = 1L;

    public ShowGraph(final String title, double[] x, double[] y) {
        super(title);
        final XYDataset dataset = createDataset(x,y);
        final JFreeChart chart = createChart(dataset);
        final ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(500, 270));
        setContentPane(chartPanel);
    }
    
    private XYDataset createDataset(double[] x, double[] y) {
	        
	        final XYSeries series1 = new XYSeries("First");
	        for(int i=0; i<x.length; i++){
	        	series1.add(x[i], y[i]);
	        }

	        /*
	        final XYSeries series2 = new XYSeries("Second");
	        series2.add(1.0, 5.0);
	        series2.add(2.0, 7.0);
	        series2.add(3.0, 6.0);
	        series2.add(4.0, 8.0);
	        series2.add(5.0, 4.0);
	        series2.add(6.0, 4.0);
	        series2.add(7.0, 2.0);
	        series2.add(8.0, 1.0);
	         */
	        final XYSeriesCollection dataset = new XYSeriesCollection();
	        dataset.addSeries(series1);
	        //dataset.addSeries(series2);
	                
	        return dataset;
	        
	    }
	    
	    private JFreeChart createChart(final XYDataset dataset) {
	        
	        // create the chart...
	        final JFreeChart chart = ChartFactory.createXYLineChart(
	            "Line Chart Demo 6",      // chart title
	            "X",                      // x axis label
	            "Y",                      // y axis label
	            dataset,                  // data
	            PlotOrientation.VERTICAL,
	            true,                     // include legend
	            true,                     // tooltips
	            false                     // urls
	        );

	        // NOW DO SOME OPTIONAL CUSTOMISATION OF THE CHART...
	        chart.setBackgroundPaint(Color.white);

//	        final StandardLegend legend = (StandardLegend) chart.getLegend();
	  //      legend.setDisplaySeriesShapes(true);
	        
	        // get a reference to the plot for further customisation...
	        final XYPlot plot = chart.getXYPlot();
	        plot.setBackgroundPaint(Color.lightGray);
	    //    plot.setAxisOffset(new Spacer(Spacer.ABSOLUTE, 5.0, 5.0, 5.0, 5.0));
	        plot.setDomainGridlinePaint(Color.white);
	        plot.setRangeGridlinePaint(Color.white);
	        
	        final XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
	        renderer.setSeriesLinesVisible(0, true);
	        renderer.setSeriesShapesVisible(1, false);
	        plot.setRenderer(renderer);

	        // change the auto tick unit selection to integer units only...
	        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
	        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
	        // OPTIONAL CUSTOMISATION COMPLETED.
	                
	        return chart;
	        
	    }

	    // ****************************************************************************
	    // * JFREECHART DEVELOPER GUIDE                                               *
	    // * The JFreeChart Developer Guide, written by David Gilbert, is available   *
	    // * to purchase from Object Refinery Limited:                                *
	    // *                                                                          *
	    // * http://www.object-refinery.com/jfreechart/guide.html                     *
	    // *                                                                          *
	    // * Sales are used to provide funding for the JFreeChart project - please    * 
	    // * support us so that we can continue developing free software.             *
	    // ****************************************************************************
	    
	    public static void main(final String[] args) {
	    	
	    	double[] x = {1d,2d,3d,4d,5d}; double[] y = {2d,5d,10d,1d,2d};
	        final ShowGraph sg = new ShowGraph("Line Chart", x,y);
	        sg.pack();
	        RefineryUtilities.centerFrameOnScreen(sg);
	        sg.setVisible(true);
	    }	    
}