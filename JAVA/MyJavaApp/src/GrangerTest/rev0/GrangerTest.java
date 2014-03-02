package GrangerTest.rev0;

import java.io.BufferedReader; 

import java.io.FileNotFoundException; 
import java.io.FileReader;
import java.io.FileWriter;
import java.io.StreamTokenizer;
import java.io.IOException;
import java.io.File;
import java.util.*;

import org.omg.CORBA.SystemException;
import ChangePoinstsDetection.MakeGraph;
import Jama.*;
import be.ac.ulg.montefiore.run.distributions.MultiGaussianDistribution;


public class GrangerTest {
	private static int k = 2;
	private static final int DATA_NUM=2;
	private static int T=0;
	
	public static void test(){
		double[][] y = new double[DATA_NUM][];
		for(int i=0; i<DATA_NUM; i++){
			//y[i]=FileIO.GetData("inp"+ (i+(int)1) +".txt");
			y[i]=FileIO.GetData("test"+ (i+(int)1) +".txt");
			//y[i]=FileIO.GetData("in"+ (i+(int)1) +".txt");
		}
				
		// データ長の比較
        if (y[0].length != y[1].length){
            throw new IllegalArgumentException("ERROR! Data length is not equal.");
        }
        System.out.println("creating matrix.");

        double[][][] ydiff = getDiffData(y); //t-kの添字の場合のtに当たるデータの作成(k,j,t)
        
        double[][] ovmat = getMatOfObservedValue(ydiff);
        double[] yvec = getVecOfY(y);
        double[][] ovmatForCnstr = getMatOfObservedValueForConstraint(ydiff);
        
        Matrix X = new Matrix(ovmat); //制約なしの場合の観測値行列
        Matrix XforCnstr = new Matrix(ovmatForCnstr); //制約ありの場合の観測値行列
        Matrix Y = new Matrix(yvec, yvec.length); //被説明変数ベクトル
        Matrix tmp = X.transpose().times(X).inverse();
        Matrix tmp_y = tmp.times(X.transpose());
        Matrix beta = tmp_y.times(Y);
        
//        LinearAlgebra.printMat(ovmatForCnstr);
        for(int i=0; i<beta.getArrayCopy().length; i++){
        	System.out.println(beta.getArrayCopy()[i][0]);
        }
        /*
    	double[] avg = LinearAlgebra.applyAVGMat(y ,0); //行について平均値を取得        
        double[] var = LinearAlgebra.applyVarMat(y);
        
        double[][][] kcov = getKCov(y, ydiff, avg); // lowの算出に使用する.k次自己共分散関数.階差×2×2
        double[][] cov = getCov(y, avg); // lowの算出に使用する.k次自己共分散関数.階差×2×2
     
        
        double[][] D = LinearAlgebra.creatDiagFromVec( 
        					LinearAlgebra.powVec(var, -0.5) );
        
        double[][][] low = getLow(D, kcov);  // low0はlowの配列では保持しない
        //double[] mu = getMu(y);        
        double[][][] fai = calcFai(low);
        */
//        MultiGaussianDistribution gaussian = new MultiGaussianDistribution(avg, cov);
        //制約ありの場合と制約無しの場合の予測値の計算
        System.out.println("getting prediction data.");
        double[][] yhat = X.times(beta).getArrayCopy(); //縦ベクトル
        double[][] yhatWithCnstr = XforCnstr.times(beta).getArrayCopy(); //縦ベクトル
        
        System.out.println("got prediction data.");
        
        // ここからSSR(残差)の計算
        double[] SSR1 = calcSSR(yvec, yhat); //制約無しの場合の残差
        double[] SSR0 = calcSSR(yvec, yhatWithCnstr); //線形制約ありの場合の残差。詳しい説明は府大鹿野#15参照
        
		// F検定で使用するT（データ数を取得）
		T = y[0].length;
		
		//Granger testの実施
		boolean[] res = test(SSR1, SSR0, T);

	    for(int i=0; i<res.length; i++){
	    	System.out.println("data"+(DATA_NUM - i)+" → data"+(i+1)+"の因果:"+res[i]);
	    }
        
        
//        FileIO.WriteFile(yhat);
        
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
//				System.out.println(i+"="+yhat[i+t*DATA_NUM][0]+" "+ y[i+t*DATA_NUM]);
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
			System.out.println(fval[i]);
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
	/*
	// 自己相関係数の算出
	public static double[][][] getLow(double[][] D, double[][][] cov){
		double[][][] res = new double[cov.length][D.length][];
		for(int i=0; i<cov.length; i++){			
			res[i] = LinearAlgebra.dotMat(
						LinearAlgebra.dotMat(D,cov[i]) , D);
		}
		return res;
	}
	
	// k次自己共分散の算出
	public static double[][][] getKCov(double[][] y, double[][][] ydiff, double[] avg){
		double[][][] res = new double[ydiff.length][ydiff[0].length][ydiff[0].length];
		
		for(int i=0; i<ydiff.length; i++){ //kの数
			double[] avediff = LinearAlgebra.applyAVGMat(ydiff[i],0); //行について平均値取得

			// 平均値と各値の差を取得
			for(int j=0; j<ydiff[i].length; j++){
				ydiff[i][j] = LinearAlgebra.addCnstVec(-1*avediff[j], ydiff[i][j]); //ydiffはtにあたる
				y[j] = LinearAlgebra.addCnstVec(-1*avg[j], y[j]); // yはt-kにあたる
			}
			
			for(int l=0; l<y.length; l++){ //データの個数
				for(int m=0; m<y.length; m++){ //データの個数
					double sum = 0.0;
					for(int t=0; t<ydiff[i][0].length; t++){
						sum += ydiff[i][l][t]*y[m][t]; //
					}
					res[i][l][m] = sum/ydiff[i][0].length;					
				}
			}
		}
		return res;
	}

	// 共分散行列の算出
	public static double[][] getCov(double[][] y, double[] avg){
		double[][] res = new double[y.length][y.length];
		
		for(int i=0; i<y.length; i++){
			for(int j=0; j<y.length; j++){
				double sum = 0.0;
				for(int t=0; t<y[i].length; t++){
						sum += (y[i][t]- avg[i])*(y[j][t] - avg[j]); //
				}
				res[i][j] = sum/y[i].length;
			}
		}
		return res;
	}
	*/
	
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
 
	/*
	// yule-walker方程式を解く（faiの推定）
	public static double[][][] calcFai(double[][][] low){
		double[][][] res = new double[low.length][low[0].length][]; // (k,y.length,y.length)
		double[][] eye = new double[low[0].length][low[0].length];
		eye = LinearAlgebra.creatDiag(eye); //単位行列の作成
		
		if(low.length==1){
			res[0]=low[0];
		}else if(low.length==2){
			double[][] tlow0 = LinearAlgebra.transposition(low[0]);
			double[][] low2 = LinearAlgebra.multMat(low[0], low[0]);
			double[][] tlowClow = LinearAlgebra.multMat( tlow0, low[0] );
			double[][] numerator = LinearAlgebra.addMat( low[1],
									LinearAlgebra.cnstMultMat( -1, low2) );
			double[][] denominator = LinearAlgebra.addMat(eye,
										LinearAlgebra.cnstMultMat(-1, tlowClow));
			
			Matrix denom = new Matrix(denominator);
			Matrix nume = new Matrix(numerator);
			Matrix mlow = new Matrix(low[0]);
			Matrix tlow = mlow.transpose();
			
			//res[1] = denom.inverse().times(nume).getArrayCopy();
			Matrix res1 = denom.inverse().times(nume);
			res[0] = mlow.minus( res1.times(tlow) ).getArrayCopy();
			res[1] = res1.getArrayCopy();
		}
		return res;
	}	
	
	//muの推定
	public static double[] getMu(double[][] x){
		double[] muhat = new double[x.length];
		for(int yi=0; yi<x.length; yi++){
			double sum=0.0;
			for(int i=k; i<x[yi].length; i++){
				sum += x[yi][i];
			}
			muhat[yi] = sum/(x[yi].length-k);
		}
		return muhat;
	}		
	
	// 制約なしの場合のyの推定値の算出
	public static double[][] calcYhatWithoutConstraint(
			double[][][] ydiff, double[][][] fai, double[] mu,
			MultiGaussianDistribution gaussian)
	{
		double[][] res = new double[ydiff[k-1][0].length][ydiff[k-1][0].length];
		double[] r = new double[ydiff.length];
		
		for(int i=0; i<ydiff.length; i++){
			for(int t=0; t<ydiff[k-1][0].length; t++){
				for(int ks=0; ks<fai.length; ks++){
					for(int it=0; it<ydiff.length; it++){
						//res[i][t] += (ydiff[it][ks][t] - mu[i])*fai[ks][i][it];
						res[i][t] += (ydiff[it][ks][t])*fai[ks][i][it];
					}
				}
		        r = gaussian.generate();
				res[i][t] += mu[i] + r[i];
		        //res[i][t] += r[i];
			}
		}
		return res;
	}

	// 制約ありの場合のyの推定値の算出
	public static double[][] calcYhatWithConstraint(
			double[][][] ydiff, double[][][] fai, double[] mu,
			MultiGaussianDistribution gaussian)
	{
		double[][] res = new double[ydiff[k-1][0].length][];
		double[] r = new double[ydiff.length];
		
		for(int i=0; i<ydiff.length; i++){
			for(int t=0; t<ydiff[k-1][0].length; t++){
				for(int ks=0; ks<fai.length; ks++){
					res[i][t] += (ydiff[i][ks][t] - mu[i])*fai[ks][i][i] ;
				}
		        r = gaussian.generate();
				res[i][t] += mu[i] + r[i];
			}
		}
		return res;	
	}	
	*/
}