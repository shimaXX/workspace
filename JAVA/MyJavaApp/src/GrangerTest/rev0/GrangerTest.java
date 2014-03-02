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
				
		// �f�[�^���̔�r
        if (y[0].length != y[1].length){
            throw new IllegalArgumentException("ERROR! Data length is not equal.");
        }
        System.out.println("creating matrix.");

        double[][][] ydiff = getDiffData(y); //t-k�̓Y���̏ꍇ��t�ɓ�����f�[�^�̍쐬(k,j,t)
        
        double[][] ovmat = getMatOfObservedValue(ydiff);
        double[] yvec = getVecOfY(y);
        double[][] ovmatForCnstr = getMatOfObservedValueForConstraint(ydiff);
        
        Matrix X = new Matrix(ovmat); //����Ȃ��̏ꍇ�̊ϑ��l�s��
        Matrix XforCnstr = new Matrix(ovmatForCnstr); //���񂠂�̏ꍇ�̊ϑ��l�s��
        Matrix Y = new Matrix(yvec, yvec.length); //������ϐ��x�N�g��
        Matrix tmp = X.transpose().times(X).inverse();
        Matrix tmp_y = tmp.times(X.transpose());
        Matrix beta = tmp_y.times(Y);
        
//        LinearAlgebra.printMat(ovmatForCnstr);
        for(int i=0; i<beta.getArrayCopy().length; i++){
        	System.out.println(beta.getArrayCopy()[i][0]);
        }
        /*
    	double[] avg = LinearAlgebra.applyAVGMat(y ,0); //�s�ɂ��ĕ��ϒl���擾        
        double[] var = LinearAlgebra.applyVarMat(y);
        
        double[][][] kcov = getKCov(y, ydiff, avg); // low�̎Z�o�Ɏg�p����.k�����ȋ����U�֐�.�K���~2�~2
        double[][] cov = getCov(y, avg); // low�̎Z�o�Ɏg�p����.k�����ȋ����U�֐�.�K���~2�~2
     
        
        double[][] D = LinearAlgebra.creatDiagFromVec( 
        					LinearAlgebra.powVec(var, -0.5) );
        
        double[][][] low = getLow(D, kcov);  // low0��low�̔z��ł͕ێ����Ȃ�
        //double[] mu = getMu(y);        
        double[][][] fai = calcFai(low);
        */
//        MultiGaussianDistribution gaussian = new MultiGaussianDistribution(avg, cov);
        //���񂠂�̏ꍇ�Ɛ��񖳂��̏ꍇ�̗\���l�̌v�Z
        System.out.println("getting prediction data.");
        double[][] yhat = X.times(beta).getArrayCopy(); //�c�x�N�g��
        double[][] yhatWithCnstr = XforCnstr.times(beta).getArrayCopy(); //�c�x�N�g��
        
        System.out.println("got prediction data.");
        
        // ��������SSR(�c��)�̌v�Z
        double[] SSR1 = calcSSR(yvec, yhat); //���񖳂��̏ꍇ�̎c��
        double[] SSR0 = calcSSR(yvec, yhatWithCnstr); //���`���񂠂�̏ꍇ�̎c���B�ڂ��������͕{�厭��#15�Q��
        
		// F����Ŏg�p����T�i�f�[�^�����擾�j
		T = y[0].length;
		
		//Granger test�̎��{
		boolean[] res = test(SSR1, SSR0, T);

	    for(int i=0; i<res.length; i++){
	    	System.out.println("data"+(DATA_NUM - i)+" �� data"+(i+1)+"�̈���:"+res[i]);
	    }
        
        
//        FileIO.WriteFile(yhat);
        
        System.out.println("Done.");
	}
	
	// �ϑ��l�s��̍쐬
	public static double[][] getMatOfObservedValue(double[][][] ydiff){
		int colNum = (k*DATA_NUM+1)*DATA_NUM;
		int rowNum = ydiff[ydiff.length-1][0].length*DATA_NUM; //max�̊K���̎��n��f�[�^��.(T-k)*2�̃f�[�^
		int t_max = ydiff[ydiff.length-1][0].length;
		double[][] res = new double[rowNum][colNum];
		
		int block = DATA_NUM; //block�̑傫��
		for(int t=0; t<t_max; t++){
			// �u���b�N���Ƀf�[�^���쐬����
			for(int i=0; i<k; i++){ // �K�������Ƀu���b�N���쐬
				for(int l=0; l<DATA_NUM; l++){
					for(int j=0; j<DATA_NUM; j++){ //�f�[�^�̌����̏c���̐����s��̍쐬
						res[block*t+j][block*block*i+l*block+j] = ydiff[i][l][t];
					}
				}
			}
			// �萔������ǉ�
			for(int j=0; j<DATA_NUM; j++){
				res[block*t+j][block*block*k+j] = 1;
			}
		}	
		return res;
	}

	// ������ۂ������f���p�̊ϑ��f�[�^�쐬
	public static double[][] getMatOfObservedValueForConstraint(double[][][] ydiff){
		int colNum = (k*DATA_NUM+1)*DATA_NUM;
		int rowNum = ydiff[ydiff.length-1][0].length*DATA_NUM; //max�̊K���̎��n��f�[�^��.(T-k)*2�̃f�[�^
		int t_max = ydiff[ydiff.length-1][0].length;
		double[][] res = new double[rowNum][colNum];
		
		int block = DATA_NUM; //block�̑傫��
		for(int t=0; t<t_max; t++){
			// �u���b�N���Ƀf�[�^���쐬����
			for(int i=0; i<k; i++){ // �K�������Ƀu���b�N���쐬
				for(int l=0; l<DATA_NUM; l++){
					for(int j=0; j<DATA_NUM; j++){ //�f�[�^�̌����̏c���̐����s��̍쐬
						if(l==j){ // ���҂Ƃ̊ւ��̂���W��������
							res[block*t+j][block*block*i+l*block+j] = ydiff[i][l][t];
						}else{
							continue;
						}
					}
				}
			}
			// �萔������ǉ�
			for(int j=0; j<DATA_NUM; j++){
				res[block*t+j][block*block*k+j] = 1;
			}
		}	
		return res;
	}
	
	// y�̒l���W�񂵂��x�N�g���̍쐬
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
	
	//SSR�̎Z�o
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

	//�O�����W���[test
	public static boolean[] test(double[] SSR1, double[] SSR0, int T){
		// ���R�x1�`6�ɂ�����5%�J�C2��l
		double[] kai2 = {3.84, 5.99, 7.81, 9.49, 11.1, 12.6};
		
		boolean[] res = new boolean[SSR1.length];
		
		Matrix ssr1 = new Matrix(SSR1, 1);
		Matrix ssr0 = new Matrix(SSR0, 1);
		
		// F�e�X�g�̎��{
		double[] fval = Ftest(ssr1, ssr0);
		for(int i=0; i<fval.length; i++){
			System.out.println(fval[i]);
			res[i] = fval[i]>kai2[k-1]; //Ftest��m1�ŏ��Z���ĂȂ��̂�m1��ς���K�v���Ȃ�
		}
		return res;
	}
	
	
	//Ftest
	public static double[] Ftest(Matrix ssr1, Matrix ssr0){
		//int m1 = k; //���R�xm1
		int m2 = T - (k*DATA_NUM+1); //���R�xm2
		
		// m1�͎Z�o��ɍēx�ς���̂ŏ��Z����Ȃ���
		return ssr0.minus(ssr1).arrayRightDivide(ssr1).times( (double)m2 ).getArrayCopy()[0];
	}
	/*
	// ���ȑ��֌W���̎Z�o
	public static double[][][] getLow(double[][] D, double[][][] cov){
		double[][][] res = new double[cov.length][D.length][];
		for(int i=0; i<cov.length; i++){			
			res[i] = LinearAlgebra.dotMat(
						LinearAlgebra.dotMat(D,cov[i]) , D);
		}
		return res;
	}
	
	// k�����ȋ����U�̎Z�o
	public static double[][][] getKCov(double[][] y, double[][][] ydiff, double[] avg){
		double[][][] res = new double[ydiff.length][ydiff[0].length][ydiff[0].length];
		
		for(int i=0; i<ydiff.length; i++){ //k�̐�
			double[] avediff = LinearAlgebra.applyAVGMat(ydiff[i],0); //�s�ɂ��ĕ��ϒl�擾

			// ���ϒl�Ɗe�l�̍����擾
			for(int j=0; j<ydiff[i].length; j++){
				ydiff[i][j] = LinearAlgebra.addCnstVec(-1*avediff[j], ydiff[i][j]); //ydiff��t�ɂ�����
				y[j] = LinearAlgebra.addCnstVec(-1*avg[j], y[j]); // y��t-k�ɂ�����
			}
			
			for(int l=0; l<y.length; l++){ //�f�[�^�̌�
				for(int m=0; m<y.length; m++){ //�f�[�^�̌�
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

	// �����U�s��̎Z�o
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
	
	// t-k�̃f�[�^�Ɗ|�����킹��t�̃f�[�^���쐬����
	public static double[][][] getDiffData(double[][] y){
        double[][][] ydiff = new double[k][y.length][y[0].length-k]; //t-k�̓Y���̏ꍇ��t�ɓ�����f�[�^�̍쐬		
		
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
	// yule-walker�������������ifai�̐���j
	public static double[][][] calcFai(double[][][] low){
		double[][][] res = new double[low.length][low[0].length][]; // (k,y.length,y.length)
		double[][] eye = new double[low[0].length][low[0].length];
		eye = LinearAlgebra.creatDiag(eye); //�P�ʍs��̍쐬
		
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
	
	//mu�̐���
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
	
	// ����Ȃ��̏ꍇ��y�̐���l�̎Z�o
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

	// ���񂠂�̏ꍇ��y�̐���l�̎Z�o
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