package GrangerTest.rev1;

import java.util.List;

public class LinearAlgebra {
	//データの標準化
	public static double[] normalize(double[] X){
		double[] res = new double[X.length];
		for(int i=0; i<X.length; i++){
			res[i] = (X[i] - meanVec(X)) / Math.sqrt( varVec(X) );
		}
		return res;
	}
			
	//List<Double> -> double[]への変換
	public static double[] ConvertDoubleArray(List<Double> list){
		double[] data = new double[list.size()];
		for(int i=0; i<list.size(); i++){
			data[i] = list.get(i);
		}
		return data;
	}
	
	public static double[] MergeArray(double[] array1, double[] array2){
		double[] mergeArray=new double[array1.length + array2.length];
	    System.arraycopy(array1, 0, mergeArray, 0, array1.length);
	    System.arraycopy(array2, 0, mergeArray, array1.length, array2.length);
	    return mergeArray;
	}
		
	//ベクトルのコピー
	public static double[] VecCopy(double[] x){
		double[] copy = new double[x.length];
		for(int i=0; i<x.length; i++){
			copy[i] = x[i];
		}
		return copy;
	}

	//行列のコピー
	public static double[][] MatCopy(double[][] x){
		double[][] copy = new double[x.length][];
		int rowLen = x.length;
		int colLen = x[0].length;
		for(int i=0; i<rowLen; i++){
			for(int j=0; j<colLen; j++){
				copy[i][j] = x[i][j];
			}
		}
		return copy;
	}
	
	// 行列の内積計算
	public static double[][] dotMat(double[][] x, double[][] y){
		double[][] res = new double[x.length][y[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<y[0].length; j++){
				res[i][j] = dotVec(x[i], getColFromMat(y, j));
			}
		}
		return res;
	}
	
	//ベクトルの内積計算
	public static double dotVec(double[] x, double[] y){
//		System.out.println(x.length);
		double res = 0.0;
		for(int i=0; i<x.length; i++){
			res += x[i]*y[i];
		}
		return res;
	}
	
	// 行列どおしの商
	public static double[][] divMat(double[][] x1, double[][] x2){
		double[][] res = new double[x1.length][x1[0].length];
		for(int i=0; i<x1.length; i++){
			for(int j=0; j<x1[0].length; j++){
				res[i][j] = x1[i][j]/x2[i][j];
			}
		}
		return res;
	}

	// 行列どおしの積
	public static double[][] multMat(double[][] x1, double[][] x2){
		double[][] res = new double[x1.length][x1[0].length];
		for(int i=0; i<x1.length; i++){
			for(int j=0; j<x1[0].length; j++){
				res[i][j] = x1[i][j]*x2[i][j];
			}
		}
		return res;
	}

	// ベクトルどおしの商
	public static double[] divVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
			res[i] = x1[i]/x2[i];
		}
		return res;
	}

	// ベクトルどおしの積
	public static double[] multVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
			res[i] = x1[i]*x2[i];
		}
		return res;
	}
	
	// 定数と行列の積
	public static double[][] cnstMultMat(double c, double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = c*x[i][j];
			}
		}
		return res;
	}
	
	// 定数と行列の列の積
	public static double[] cnstMultMatCol(double c, double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
				res[i] = c*x[i][col];
		}
		return res;
	}

	// 定数と行列の列の和
	public static double[] addCnstMatCol(double c, double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
				res[i] = c+x[i][col];
		}
		return res;
	}

	// 定数とベクトルの和
	public static double[] cnstMultVec(double c, double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = c*x[i];
		}
		return res;
	}
	
	// 行列どうしの和
	public static double[][] addMat(double[][] x1, double[][] x2){
		if(x1.length!=x2.length || x1[0].length!=x2[0].length){
			throw new IllegalArgumentException("Error! Data length is not equal.");
		}
		double[][] res = new double[x1.length][x1[0].length];
		for(int i=0; i<x1.length; i++){
			for(int j=0; j<x1[0].length; j++){
				res[i][j] = x1[i][j] + x2[i][j];
			}
		}
		return res;
	}

	// ベクトルどうしの和
	public static double[] addVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
				res[i] = x1[i] + x2[i];
		}
		return res;
	}

	// 定数と行列の和
	public static double[][] addCnstMat(double c, double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = c+x[i][j];
			}
		}
		return res;
	}

	// 定数とベクトルの和
	public static double[] addCnstVec(double c, double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = c+x[i];
		}
		return res;
	}
	
	// 行列から列を取り出す
	public static double[] getColFromMat(double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = x[i][col];
		}
		return res;
	}

	// 行列全体をexpする
	public static double[][] expMat(double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = Math.exp(x[i][j]);
			}
		}
		return res;
	}

	// 行列全体をlogする
	public static double[][] logMat(double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = Math.log(x[i][j]);
			}
		}
		return res;
	}

	// ベクトルをlogする
	public static double[] logVec(double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = Math.log(x[i]);
		}
		return res;
	}

	// ベクトルをn乗する
	public static double[] powVec(double[] x, double n){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = Math.pow(x[i], n);
		}
		return res;
	}
	
	// 列のみの代入（コピー）
	public static double[][] copyCol(double[] x1, double[][] x2, int col){
		for(int i=0; i<x1.length; i++){
			x2[i][col] = x1[i];
		}
		return x2;
	}	

	// 転置
	public static double[][] transposition(double[][] x){
		double[][] res = new double[x[0].length][x.length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[j][i] = x[i][j];
			}
		}
		return res;
	}
	
	// 行列全体の和を求める
	public static double sumMat(double[][] x){
		double res = 0.0;
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res += x[i][j];
			}
		}
		return res;
	}
	
	// 行列の行または列の和を求める
	public static double[] applySumMat(double[][] x, int axis){
		double[] res = null;
		
		// 列についての和を求める
		if(axis==1){
			res = new double[x[0].length];
			for(int col=0; col<x[0].length; col++){
				for(int row=0; row<x.length; row++){
					res[col] += x[row][col];
				}
			}
		} 		
		// 行についての和を求める
		else if(axis==0){
			res = new double[x.length];
			for(int row=0; row<x.length; row++){
				for(int col=0; col<x[0].length; col++){
					res[row] += x[row][col];
				}
			}
		} 
		return res;
	}

	// 行列の行の平均値を求める
	public static double[] applyAVGMat(double[][] x, int axis){
		double[] res = null;
		double[] ln = new double[x.length];
		
		for(int i=0; i<x.length; i++){
			ln[i] = x[i].length;
		}

		res = applySumMat(x, axis);
		res = divVec(res, ln);
		
		return res;
	}

	// 行列の行の分散を求める
	public static double[] applyVarMat(double[][] x){
		double[] res = new double[x.length];
		
		for(int i=0; i<x.length; i++){
			res[i] = varVec(x[i]);
		}

		return res;
	}
	
	// ベクトル全体の和を求める
	public static double sumVec(double[] x){
		double res = 0.0;
		for(int i=0; i<x.length; i++){
			res += x[i];
		}
		return res;
	}

	//ベクトルの分散の計算
	public static double varVec(double[] X){
		double var =0.0;
		double total=0.0;
		double lngt = X.length;
		double avg = meanVec(X);
		for(int i=0; i<lngt; i++){
			total += Math.pow(X[i]-avg,2.0d);
		}
		var = total/lngt;
		return var;
	}
	
	//ベクトルの平均の計算
	public static double meanVec(double[] X){
		double sum = sumVec(X);
		return sum/X.length;
	}
	
	// すでに存在する0行列から単位行列を作る
	public static double[][] creatDiag(double[][] x){
		double[][] res = new double[x.length][x[0].length];
		int len=x.length;
		
		if(x.length > x[0].length) {len=x[0].length;}
		for(int i=0; i<len; i++){
			res[i][i] = 1;
		}
		return res;
	}
	
	// 既に存在するベクトルから対角行列を作る
	public static double[][] creatDiagFromVec(double[] x){
		double[][] res = new double[x.length][x.length];

		for(int i=0; i<x.length; i++){
			res[i][i] = x[i];
		}
		return res;
	}
	
	// 行列のコンソール出力
	public static void printMat(double[][] x){
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				System.out.print(x[i][j]+" ");
			}
			System.out.println();
		}
	}
}
