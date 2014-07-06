package GrangerTest;

public class Main {
	public static void main(String[] args){
		int DATA_NUM=3;
		double[][] y = new double[DATA_NUM][];
		for(int i=0; i<DATA_NUM; i++){
			y[i]=FileIO.GetData("test"+ (i+(int)1) +".txt");
		}
		
		int k=3;
		GrangerTest.test(y, k);
	}
}
