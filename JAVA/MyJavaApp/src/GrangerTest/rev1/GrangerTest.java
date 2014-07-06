package GrangerTest.rev1;

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
			y[i]=FileIO.GetData("test"+ (i+(int)1) +".txt");
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
			System.out.println("F-value of func"+(i+1)+":"+fval[i]);
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
}