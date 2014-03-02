package BehaviorAnalysis;

import java.util.*;
import java.math.*;
import java.io.IOException;

public class LinearAlgebra {
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

	// 行列の行または列の平均値を求める
	public static double[] applyAVGMat(double[][] x, int axis){
		double[] res = null;
		double[] len = null;
		
		for(int i=0; i<x.length; i++){
			len[i] = x[i].length;
		}

		res = applyAVGMat(x, axis);
		res = divVec(res, len);
		
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
}
