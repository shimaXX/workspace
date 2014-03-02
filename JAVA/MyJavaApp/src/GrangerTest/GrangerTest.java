package GrangerTest;

import java.util.*;
import Jama.*;

public class GrangerTest {
	private static int k;
	private static int DATA_NUM;
	private static int T=0;
		
	public static void test(double[][] inpdata, int kaisa){
		k = kaisa;
		
		double[][] y = inpdata;
		DATA_NUM = y.length;
		
		// データ長の比較
        if (y[0].length != y[1].length){
            throw new IllegalArgumentException("ERROR! Data length is not equal.");
        }
        System.out.println("creating matrix.");

        double[][][] ydiff = getDiffData(y); //t-kの添字の場合のtに当たるデータの作成(k,j,t)
        
        double[][] ovmat = getMatOfObservedValue(ydiff);
        double[] yvec = getVecOfY(y);
        //double[][] ovmatForCnstr = getMatOfObservedValueForConstraint(ydiff);
        
        Matrix X = new Matrix(ovmat); //制約なしの場合の観測値行列
        //Matrix XforCnstr = new Matrix(ovmatForCnstr); //制約ありの場合の観測値行列
        Matrix Y = new Matrix(yvec, yvec.length); //被説明変数ベクトル
        Matrix tmp = X.transpose().times(X).inverse();
        Matrix tmp_y = tmp.times(X.transpose());
        Matrix beta = tmp_y.times(Y);
        
        //制約ありの場合の係数ベクトルの作成
        double[][] betaForCnstr = makeBetaForCnstr(beta.getRowPackedCopy());
        
        //LinearAlgebra.printMat(betaForCnstr);
        
        //制約ありの場合と制約無しの場合の予測値の計算
        System.out.println("getting prediction data.");
        double[][] yhat = X.times(beta).getArrayCopy(); //縦ベクトル
        
        int cmbnum = DATA_NUM*(DATA_NUM-1); 
        double[][][] yhatWithCnstr = new double[cmbnum][y[0].length-k][];
        for(int i=0; i<cmbnum; i++){
    		Matrix betatmp = new Matrix(betaForCnstr[i], betaForCnstr[i].length);
    		yhatWithCnstr[i] = X.times(betatmp).getArrayCopy(); //縦ベクトル
        }
        
        System.out.println("got prediction data.");
        
        // ここからSSR(残差)の計算
        double[] SSR1 = calcSSR(yvec, yhat); //制約無しの場合の残差
        double[][] SSR0 = new double[cmbnum][];
        for(int i=0; i<cmbnum; i++){
        	SSR0[i] = calcSSR(yvec, yhatWithCnstr[i]); //線形制約ありの場合の残差。詳しい説明は府大鹿野#15参照
        }
        
		// F検定で使用するT（データ数を取得）
		T = y[0].length;
		
		//Granger testの実施
		boolean[] res = new boolean[cmbnum];
		int itr = 0;
		for(int i=0; i<DATA_NUM; i++){
			for(int j=0; j<DATA_NUM; j++){
				if(i!=j){
					System.out.println( "loop="+(itr+1) );
					res[itr] = test(SSR1, SSR0[itr], T)[j];
					itr += 1;
				}
			}
		}
			
		itr=0;
	    for(int i=0; i<DATA_NUM; i++){
	    	for(int j=0; j<DATA_NUM; j++){
	    		if(i!=j){
	    			System.out.println("data"+(i+1)+" → data"+(j+1)+"の因果:"+res[itr]);
	    			itr+=1;
	    		}
	    	}
	    }
                
        System.out.println("Done.");
	}
	
	// 観測値行列の作成
	public static double[][] getMatOfObservedValue(double[][][] ydiff){
		int colNum = (k*DATA_NUM+1)*DATA_NUM;
		int rowNum = ydiff[ydiff.length-1][0].length*DATA_NUM; //maxの階差の時系列データ分.(T-k)*2個のデータ
		int t_max = ydiff[ydiff.length-1][0].length;
		double[][] res = new double[rowNum][colNum];
		
		int block = DATA_NUM; //blockの大きさ
		for(int t=0; t<t_max; t++){
			// ブロック毎にデータを作成する
			for(int i=0; i<k; i++){ // 階差分横にブロックを作成
				for(int l=0; l<DATA_NUM; l++){
					for(int j=0; j<DATA_NUM; j++){ //データの個数分の縦横の正方行列の作成
						res[block*t+j][block*block*i+l*block+j] = ydiff[i][l][t];
					}
				}
			}
			// 定数部分を追加
			for(int j=0; j<DATA_NUM; j++){
				res[block*t+j][block*block*k+j] = 1;
			}
		}	
		return res;
	}

	// 制約を課したモデル用の観測データ作成
	public static double[][] getMatOfObservedValueForConstraint(double[][][] ydiff){
		int colNum = (k*DATA_NUM+1)*DATA_NUM;
		int rowNum = ydiff[ydiff.length-1][0].length*DATA_NUM; //maxの階差の時系列データ分.(T-k)*2個のデータ
		int t_max = ydiff[ydiff.length-1][0].length;
		double[][] res = new double[rowNum][colNum];
		
		int block = DATA_NUM; //blockの大きさ
		for(int t=0; t<t_max; t++){
			// ブロック毎にデータを作成する
			for(int i=0; i<k; i++){ // 階差分横にブロックを作成
				for(int l=0; l<DATA_NUM; l++){
					for(int j=0; j<DATA_NUM; j++){ //データの個数分の縦横の正方行列の作成
						if(l==j){ // 他者との関わりのある係数を除く
							res[block*t+j][block*block*i+l*block+j] = ydiff[i][l][t];
						}else{
							continue;
						}
					}
				}
			}
			// 定数部分を追加
			for(int j=0; j<DATA_NUM; j++){
				res[block*t+j][block*block*k+j] = 1;
			}
		}	
		return res;
	}
	
	// yの値を集約したベクトルの作成
	public static double[] getVecOfY(double[][] y){
		int t_max = y.length*y[0].length-k*y.length;
		
		double[] res = new double[t_max];
		for(int t=k; t<y[0].length; t++){
			for(int i=0; i<y.length; i++){
				res[(t-k)*y.length+i] = y[i][t];
			}
		}
		return res;
	}
	
	//SSRの算出
	public static double[] calcSSR(double[] y, double[][] yhat){
		double[] res = new double[DATA_NUM];
		
		for(int i=0; i<DATA_NUM; i++){
			for(int t=0; t<y.length/DATA_NUM; t++){
				res[i] += Math.pow( yhat[i+t*DATA_NUM][0]-y[i+t*DATA_NUM], 2 );
			}
		}
		return res;
	}

	//グレンジャーtest
	public static boolean[] test(double[] SSR1, double[] SSR0, int T){
		// 自由度1～6における5%カイ2乗値
		double[] kai2 = {3.84, 5.99, 7.81, 9.49, 11.1, 12.6};
		
		boolean[] res = new boolean[SSR1.length];
		
		Matrix ssr1 = new Matrix(SSR1, 1);
		Matrix ssr0 = new Matrix(SSR0, 1);
		
		// Fテストの実施
		double[] fval = Ftest(ssr1, ssr0);
		for(int i=0; i<fval.length; i++){
			System.out.println("F-value of func"+(i+1)+":"+fval[i]);
			res[i] = fval[i]>kai2[k-1]; //Ftestでm1で除算してないのでm1を積する必要がない
		}
		return res;
	}
	
	//Ftest
	public static double[] Ftest(Matrix ssr1, Matrix ssr0){
		//int m1 = k; //自由度m1
		int m2 = T - (k*DATA_NUM+1); //自由度m2
		
		// m1は算出後に再度積するので除算から省いた
		return ssr0.minus(ssr1).arrayRightDivide(ssr1).times( (double)m2 ).getArrayCopy()[0];
	}
	
	// t-kのデータと掛け合わせるtのデータを作成する
	public static double[][][] getDiffData(double[][] y){
        double[][][] ydiff = new double[k][y.length][y[0].length-k]; //t-kの添字の場合のtに当たるデータの作成		
		
	    for(int i=1; i<=k; i++){
	    	for(int j=0; j<y.length; j++){
	    		int itr = 0;
	    		for(int t=k-i; t<y[0].length-i; t++){
	    			ydiff[i-1][j][itr] = y[j][t];
	    			itr+=1;
	    		}
	    	}
	    }
	    return ydiff;
	}
	
	// 制約用のbetaベクトルの作成
	public static double[][] makeBetaForCnstr(double[] beta){
		int cmbnum = DATA_NUM*(DATA_NUM-1);
		int kblock = DATA_NUM*DATA_NUM;
		
		double[][] res = new double[cmbnum][]; //格納は1→2,1→3,...,2→1,2→3...の順
		
		for (int i=0; i<res.length; i++) {
			res[i] = Arrays.copyOf(beta, beta.length); //全ての行にbetaをコピーしておく
		}
		
		for(int ki=0; ki<k; ki++){ //最外層のブロック
			int cmbn = 0;
			for(int i=0; i<DATA_NUM; i++){ //内側のブロック
				for(int j=0; j<DATA_NUM; j++){ //ブロックの中
					if(i!=j){
						res[cmbn][kblock*ki+i*DATA_NUM+j] = 0;
						cmbn += 1;
					}
				}
			}
		}
		return res;
	}
}