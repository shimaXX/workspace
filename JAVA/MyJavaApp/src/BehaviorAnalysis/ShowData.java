package BehaviorAnalysis;

public class ShowData {
	public static void showMat(double[][] x){
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				System.out.print(x[i][j]);
				if(j==x[0].length-1) System.out.println();
				else System.out.print(" ,");
			}
		}
	}
	
	public static void showVec(double[] x){
		for(int i=0; i<x.length; i++){
			System.out.print(x[i]);
			if(i==x.length-1) System.out.println();
			else System.out.print(" ,");
		}
	}
	
	
	
}
