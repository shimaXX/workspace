package BehaviorAnalysis;

import java.util.*;
import java.math.*;
import BehaviorAnalysis.LinearAlgebra;
import BehaviorAnalysis.MNL;
import BehaviorAnalysis.ShowData;


public class LogitModel {
	private static MNL MNL = new MNL();
	private static LinearAlgebra LA = new LinearAlgebra();
	private static ShowData SD = new ShowData();
	private int hh = 100;
	private int pt = 20;

	private Map<String, double[][]> data = new HashMap<String, double[][]>();
	private double[] betas = null;
	private double[][] buy = null;
	private double[][] price = null;
	private double[][] disp = null;
	
	LogitModel(){
		this.data = MNL.createData();
		this.betas = data.get("betas")[0];
		this.buy = data.get("buy");
		this.price = data.get("price");
		this.disp = data.get("disp");
	}
	
	public void estimParam(){
		double eps, H[][], step, beta0[], dx[], y[];
		int fun, i1, max, method, n, opt_1, sw = 0;
		
		/*
		 関数 3 変数の数 2 最大試行回数 200 一次元最適化 1
		 方法 1 許容誤差 1.0e-10 刻み幅 0.09
		 初期値 0.0 0.0 ← xの初期値.最適化する変数はここでは2なので初期値も2つ.		
		*/
		
		fun = 4; n=5; max=10000; opt_1=1;
		method=1; eps=1.0e-10; step=0.007;
				
		beta0  = new double [n]; Arrays.fill(beta0,0.0); //例内のxのこと
		dx = new double [n];
		y  = new double [1];
		H  = new double [n][n];
		
		// 実行
		BFGSkansu kn = new BFGSkansu(fun, n, this.buy, this.price, this.disp);
		sw = BFGS.DFP_BFGS(method, opt_1, max, n, eps, step, y, beta0, dx, H, kn);
		
		
		// 結果の出力
		if (sw < 0) {
			System.out.print("   収束しませんでした！");
			switch (sw) {
				case -1:
					System.out.println("（収束回数）");
					break;
				case -2:
					System.out.print("（１次元最適化の区間）");
					break;
				case -3:
					System.out.print("（黄金分割法）");
					break;
			}
		}
		else {
			System.out.print("   結果＝");
			for (i1 = 0; i1 < n; i1++)
				System.out.print(beta0[i1] + " ");
			System.out.println(" 最小値＝" + y[0] + "  回数＝" + sw);
		}
		
		
		
	}

	public static double calcLogLKH(double[] betas, double[][] price, double[][] disp, double[][] buy){
		double[][] u = MNL.calcU(betas, price, disp);

//		System.out.println("u=");
//		ShowData.showMat(u);

		//calculate denominator
		double[][] tmp = LA.expMat(u);
		double[] d = MNL.calcD(tmp);

//		System.out.println("d=");		
//		ShowData.showVec(d);

		double[] LLI = new double[u[0].length];
		Arrays.fill(LLI, 0);
		for(int i=0; i<u.length; i++){
			LLI = LA.addVec( LLI, LA.multVec( LA.getColFromMat(buy, 0), u[0]) );
		}
		
		LLI = LA.addVec(LLI, LA.cnstMultVec(-1, LA.logVec(d)) );
		return LA.sumVec(LLI);		
	}
	
	public static double[] calcGradient(int brandnum, int cnstnum,
			double[] betas, double[][] price, double[][] disp, double[][] buy)
	{
		int datanum = price.length;
		int valnum = betas.length;
		
		double[][] pr = MNL.MNLmodel(betas, price, disp);
		double[][] si = new double[price.length][betas.length]; // 列数は微分方程式の数
		double[][] cnst = new double[brandnum][cnstnum];
		double[] x = new double[betas.length];
		
		cnst = LA.creatDiag(cnst);
		// calculate differential of log likelihood
		for(int i=0; i<datanum; i++){
			for(int j=0; j<brandnum; j++){
				// setting marketing variables
				x[0]=price[i][j]; x[1]=disp[i][j];
				x[2]=cnst[j][0]; x[3]=cnst[j][1]; x[4]=cnst[j][2];

				for(int k=0; k<betas.length; k++){
					si[i][k] += (buy[i][j] - pr[i][j])*x[k];
				}
			}
		}
		
		double[] sc = LA.applySumMat(si, 1);

		return sc;
	}
	
	public static double[][] calcHessian(int brandnum, int cnstnum,
			double[] betas, double[][] price, double[][] disp, double[][] buy)
	{
		int datanum = price.length;
		int valnum = betas.length;
		
		double[][] pr = MNL.MNLmodel(betas, price, disp);
		double[][] si = new double[price.length][betas.length]; // 列数は微分方程式の数
		double[][] cnst = new double[brandnum][cnstnum];
		double[][] x = new double[brandnum][betas.length];
		double[][] hm = new double[betas.length][betas.length]; // ヘッセ行列
		
		cnst = LA.creatDiag(cnst);
		// calculate differential of log likelihood
		for(int i=0; i<datanum; i++){
			for(int k=0; k<valnum; k++){
				for(int l=0; l<valnum; l++){
					for(int j=0; j<brandnum; j++){
						// setting marketing variables
						for(int xrow=0; xrow<x.length; xrow++){
							x[xrow][0]=price[i][xrow]; x[xrow][1]=disp[i][xrow];
							x[xrow][2]=cnst[xrow][0]; x[xrow][3]=cnst[xrow][1];
							x[xrow][4]=cnst[xrow][2];
						}								
						
						hm[k][l] += -pr[i][j]*( x[j][k] - LA.sumVec(LA.multVec(LA.getColFromMat(x, k), pr[i])) )
								*( x[j][l] - LA.sumVec(LA.multVec(LA.getColFromMat(x, l), pr[i])) );
					}
				}
			}
		}
		
		return hm;
	}	
}
