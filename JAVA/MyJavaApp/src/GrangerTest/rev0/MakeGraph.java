package GrangerTest.rev0;

import org.jfree.chart.JFreeChart;
import org.jfree.chart.ChartFactory;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.chart.plot.PlotOrientation;

import javax.swing.JFrame;
import java.awt.BorderLayout;
import org.jfree.chart.ChartPanel;


public class MakeGraph extends JFrame{
	  /**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public static void main(double[] x, double[] score) {
		  MakeGraph frame = new MakeGraph(x,score);

		  frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		  frame.setBounds(10, 10, 500, 500);
		  frame.setTitle("view result");
		  frame.setVisible(true);
	  }

	  MakeGraph(double[] x, double[] score){
		    DefaultCategoryDataset data = new DefaultCategoryDataset();
		    String[] series = {"origin", "result score"};
		    String[] category = new String[x.length];
		    for(int i=0; i<x.length; i++){
		    	category[i] = Integer.toString(i);
		    }
		    for(int i=0; i<series.length; i++){
		    	for(int j=0; j<x.length; j++){
		    		if(i==0){
		    			data.addValue(x[j], series[i], category[j]);
		    		}
		    		else{
		    			data.addValue(score[j], series[i], category[j]);
		    		}
		    	}
		    }

		    JFreeChart chart = 
		      ChartFactory.createLineChart("ƒf[ƒ^„ˆÚ",
		                                   "Step",
		                                   "value",
		                                   data,
		                                   PlotOrientation.VERTICAL,
		                                   true,
		                                   false,
		                                   false);

		    ChartPanel cpanel = new ChartPanel(chart);
		    getContentPane().add(cpanel, BorderLayout.CENTER);
	  }
}