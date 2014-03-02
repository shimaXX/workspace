package BehaviorAnalysis;

import java.math.*;
import java.util.*;
import BehaviorAnalysis.LinearAlgebra;
import BehaviorAnalysis.ShowData;


public class MNL {
	private static LinearAlgebra LN = new LinearAlgebra();
	private static ShowData SD = new ShowData();
	final private static int BRAND = 4;
		
	//define multiple logit model
	public double[][] MNLmodel(double[] betas, double[][] price, double[][] disp ){
		double[][] pr = new double[this.BRAND][price.length];
		double[][] u = calcU(betas, price, disp);
		
		//calculate denominator
		double[][] tmp = LN.expMat(u);
		double[] d = calcD(tmp);
		
		//calculate selection probability
		for(int i=0; i<this.BRAND; i++){
			pr[i] = LN.divVec(tmp[i],d);
		}

		return LN.transposition(pr);
	}

	public double[][] calcU(double[] betas, double[][] price, double[][] disp){
		double[][] u = new double[this.BRAND][price.length];

		double beta1 = betas[0];
		double beta2 = betas[1];
		double beta01 = betas[2];
		double beta02 = betas[3];
		double beta03 = betas[4];
		
		//calculate value of utility		
		double[][] priceAddBeta1 = LN.cnstMultMat(beta1, price);
		double[][] dispAddBeta2 = LN.cnstMultMat(beta2, disp);
				
		double[][] addedMat = LN.addMat(priceAddBeta1, dispAddBeta2);

		u[0] = LN.addCnstMatCol(beta01, addedMat, 0); //copy from vector to mat
		u[1] = LN.addCnstMatCol(beta02, addedMat, 1);
		u[2] = LN.addCnstMatCol(beta03, addedMat, 2);
		u[3] = LN.getColFromMat(addedMat, 3);
		
		return u;
	}
	
	public double[] calcD(double[][] tmp){
		double[] d = new double[tmp[0].length];
		Arrays.fill(d,0); // 0埋め
		
		for(int i=0; i<this.BRAND; i++){
			d = LN.addVec(d, tmp[i]);
		}
		if(d[0]==0){
			throw new IllegalArgumentException("denominator is zeros");
		}
		return d;
	}
	
	public Map<String, double[][]> createData(){
		Map<String, double[][]> data = new HashMap<String, double[][]>();
		
		// create random object
		Random rand = new Random();
		// setting seed
		rand.setSeed(555);
		
		/* setting parameter */
		double[][] betas = new double[1][5];
		betas[0][0] = -5.0; betas[0][1] = 2.0;
		betas[0][2] = 2.0; betas[0][3] = 1.0; betas[0][4] = 0.0; 
		int hh = 100; // number of family
		int pt = 20; // number of purchase
		
		int hhpt = hh*pt;
		
		double[][] id = new double[hhpt][2]; // individual id
		double[][] buy = new double[hhpt][this.BRAND]; // purchase dummy id
		double[][] price = new double[hhpt][this.BRAND]; // value
		double[][] disp = new double[hhpt][this.BRAND]; // display existence or non-existence
		
		double sp=0;
		for(int i=0; i<hh; i++){
			for(int j=0; j<pt; j++){
				int r = i*pt+j;
				id[r][0] = i;
				id[r][1] = j;

				// ブランド1の販売価格,特売陳列の有無の発生
				double rn = rand.nextDouble();
				if(rn<0.8){sp=1.0;}
				else{
					if(rn<0.95){sp=0.9;}
					else{sp=0.8;}
				}
				price[r][0]=sp;
				if(rn>0.75){disp[r][1]=1;}
				else{disp[r][0]=0;}

				// ブランド2の販売価格,特売陳列の有無の発生
				rn = rand.nextDouble();
				if(rn<0.5){sp=1.0;}
				else{
					if(rn<0.8){sp=0.8;}
					else{sp=0.6;}
				}
				price[r][1]=sp;
				if(rn>0.85){disp[r][1]=1;}
				else{disp[r][1]=0;}

				// ブランド3の販売価格,特売陳列の有無の発生
				rn = rand.nextDouble();
				if(rn<0.7){sp=1.0;}
				else{
					if(rn<0.8){sp=0.8;}
					else{sp=0.6;}
				}
				price[r][2]=sp;
				if(rn>0.55){disp[r][1]=1;}
				else{disp[r][2]=0;}
				
				// ブランド4の販売価格,特売陳列の有無の発生
				rn = rand.nextDouble();
				if(rn<0.5){sp=1.0;}
				else{
					if(rn<0.8){sp=0.8;}
					else{sp=0.6;}
				}
				price[r][3]=sp;
				if(rn>0.5){disp[r][1]=1;}
				else{disp[r][3]=0;}
			}
		}
		
		// calculate selection probability 
		double[][] ppr = MNLmodel(betas[0], price, disp);
		
		// 購買ブランドを決定
		for(int i=0; i<hhpt; i++){
			double[] csppr = cumsum(ppr[i]);
			double rn2 = rand.nextDouble();
			int ppm = whichMax(csppr, rn2);
			buy[i][ppm] =1;
		}
		
		data.put("betas", betas);
		data.put("id", id);
		data.put("buy", buy);
		data.put("price", price);
		data.put("disp", disp);

		return data;
	}
	
	// cumulative sum
	public static double[] cumsum(double[] x){
		double[] res = new double[x.length];
		for(int i=0; i<x.length; i++){
			if(i==0){res[i] = x[i];}
			else{res[i] = x[i] + res[i-1];}
		}
		return res;
	}
	
	// get min column to exceed threshold
	public static int whichMax(double[] x, double r){
		int res = 0;
		for(int i=0; i<x.length; i++){
			 if(x[i]>=r){
				 res=i;
				 break;
			 }
		}
		return res;
	}
}
