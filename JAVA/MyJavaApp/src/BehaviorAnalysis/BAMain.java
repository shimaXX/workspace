package BehaviorAnalysis;

import java.util.*;
import BehaviorAnalysis.ShowData;
import BehaviorAnalysis.MNL;
import BehaviorAnalysis.LogitModel;;



public class BAMain {
	private static MNL MNL = new MNL();		
	private static ShowData SD = new ShowData();
	private static LogitModel LM = new LogitModel();
	
	// main
	public static void main(String[] args){
		//System.out.println("LL= " + LM.estimParam());
		LM.estimParam();
	}
}
