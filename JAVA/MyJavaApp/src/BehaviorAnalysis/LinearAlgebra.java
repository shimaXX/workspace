package BehaviorAnalysis;

import java.util.*;
import java.math.*;
import java.io.IOException;

public class LinearAlgebra {
	// �s��ǂ����̏�
	public static double[][] divMat(double[][] x1, double[][] x2){
		double[][] res = new double[x1.length][x1[0].length];
		for(int i=0; i<x1.length; i++){
			for(int j=0; j<x1[0].length; j++){
				res[i][j] = x1[i][j]/x2[i][j];
			}
		}
		return res;
	}

	// �s��ǂ����̐�
	public static double[][] multMat(double[][] x1, double[][] x2){
		double[][] res = new double[x1.length][x1[0].length];
		for(int i=0; i<x1.length; i++){
			for(int j=0; j<x1[0].length; j++){
				res[i][j] = x1[i][j]*x2[i][j];
			}
		}
		return res;
	}

	// �x�N�g���ǂ����̏�
	public static double[] divVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
			res[i] = x1[i]/x2[i];
		}
		return res;
	}

	// �x�N�g���ǂ����̐�
	public static double[] multVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
			res[i] = x1[i]*x2[i];
		}
		return res;
	}
	
	// �萔�ƍs��̐�
	public static double[][] cnstMultMat(double c, double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = c*x[i][j];
			}
		}
		return res;
	}
	
	// �萔�ƍs��̗�̐�
	public static double[] cnstMultMatCol(double c, double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
				res[i] = c*x[i][col];
		}
		return res;
	}

	// �萔�ƍs��̗�̘a
	public static double[] addCnstMatCol(double c, double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
				res[i] = c+x[i][col];
		}
		return res;
	}

	// �萔�ƃx�N�g���̘a
	public static double[] cnstMultVec(double c, double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = c*x[i];
		}
		return res;
	}
	
	// �s��ǂ����̘a
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

	// �x�N�g���ǂ����̘a
	public static double[] addVec(double[] x1, double[] x2){
		double[] res = new double[x1.length];
		for(int i=0; i<x1.length; i++){
				res[i] = x1[i] + x2[i];
		}
		return res;
	}

	// �萔�ƍs��̘a
	public static double[][] addCnstMat(double c, double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = c+x[i][j];
			}
		}
		return res;
	}

	// �萔�ƃx�N�g���̘a
	public static double[] addCnstVec(double c, double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = c+x[i];
		}
		return res;
	}
	
	// �s�񂩂������o��
	public static double[] getColFromMat(double[][] x, int col){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = x[i][col];
		}
		return res;
	}

	// �s��S�̂�exp����
	public static double[][] expMat(double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = Math.exp(x[i][j]);
			}
		}
		return res;
	}

	// �s��S�̂�log����
	public static double[][] logMat(double[][] x){
		double[][] res = new double[x.length][x[0].length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[i][j] = Math.log(x[i][j]);
			}
		}
		return res;
	}

	// �x�N�g����log����
	public static double[] logVec(double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			res[i] = Math.log(x[i]);
		}
		return res;
	}
	
	// ��݂̂̑���i�R�s�[�j
	public static double[][] copyCol(double[] x1, double[][] x2, int col){
		for(int i=0; i<x1.length; i++){
			x2[i][col] = x1[i];
		}
		return x2;
	}	

	// �]�u
	public static double[][] transposition(double[][] x){
		double[][] res = new double[x[0].length][x.length];
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res[j][i] = x[i][j];
			}
		}
		return res;
	}
	
	// �s��S�̘̂a�����߂�
	public static double sumMat(double[][] x){
		double res = 0.0;
		for(int i=0; i<x.length; i++){
			for(int j=0; j<x[0].length; j++){
				res += x[i][j];
			}
		}
		return res;
	}
	
	// �s��̍s�܂��͗�̘a�����߂�
	public static double[] applySumMat(double[][] x, int axis){
		double[] res = null;
		
		// ��ɂ��Ă̘a�����߂�
		if(axis==1){
			res = new double[x[0].length];
			for(int col=0; col<x[0].length; col++){
				for(int row=0; row<x.length; row++){
					res[col] += x[row][col];
				}
			}
		} 		
		// �s�ɂ��Ă̘a�����߂�
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

	// �s��̍s�܂��͗�̕��ϒl�����߂�
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
	
	// �x�N�g���S�̘̂a�����߂�
	public static double sumVec(double[] x){
		double res = 0.0;
		for(int i=0; i<x.length; i++){
			res += x[i];
		}
		return res;
	}

	// ���łɑ��݂���0�s�񂩂�P�ʍs������
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
