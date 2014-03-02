package ChangePoinstsDetection;

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

/*
 * http://www.numericalmethod.com/trac/numericalmethod/browser/public/Examples/src/com/numericalmethod/suanshu/examples/LinearTimeSeries.java
 */

public class ChangePointsDetection {
	private static final String CURRENT_PATH = new File("").getAbsolutePath();
	private static final String PATH = CURRENT_PATH+"/works/";
	private static int term = 70;
	private static int window = 5;
//	private static List<Integer> order = Arrays.asList(1,1,0); //配列をリストに変換
//	private static double r = 0.2;
	private static int k = 1;

	/*
	ChangePointsDetection(){
		term = 70;
		window = 5;
		order = Arrays.asList(1,1,0); //配列をリストに変換
		r = 0.2;
		k = 1;
		System.out.println("term:" + term + ", window:"+window + ", order:"+order);
	}
	*/
	
	public static void main(String[] args){
		double[] X = GetData();
        long reqLength = term * 2 + window + Math.round(window*0.5) - 2;
        
        double[] scoreS1 = new double[X.length - term -1 - (window-1)];
        double[] scoreS2 = new double[X.length - (int)reqLength - 2];
        int ln = X.length - scoreS2.length;
        double[] zeroArray = new double[ln];
        double[] score = new double[X.length];
        
        if (X.length < reqLength){
            throw new IllegalArgumentException("ERROR! Data length is not enough.");
        }
        System.out.println("Scoring start.");

        X = normalize(X);
        scoreS1 = Outlier(X);
        scoreS2 = ChangePoint(scoreS1);
        for(int i=0; i<ln; i++) zeroArray[i] = 0.0;
        score = MergeArray(zeroArray, scoreS2);
        //for(int i=0; i<score.length; i++) System.out.println(score[i]+",");
        WriteFile(score);
        MakeGraph graph = new MakeGraph(X, score);
        graph.main(X, score);
        System.out.println("Done.");
	}
	
	//入力データの取得
	private static double[] GetData() throws SystemException{
//		BufferedReader br = null;
		List<Double> list = new ArrayList<>();
		
		try(BufferedReader br = new BufferedReader(new FileReader(PATH+"input/tunami01.txt")))
		{
			String line;
	
			while ((line = br.readLine()) != null) {
				//double[] intArray = convertIntArray(line);
				//double data = Double.parseDouble(line);
				if (line != null) {
					list.add(Double.parseDouble(line));
				}
			}
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		//System.out.println( (Double[])list.toArray(new Double[0]) );
		return ConvertDoubleArray(list); //listからdouble型の配列に変換
	}

	private static double[] convertIntArray(String line) {
		String[] strArray = line.split(" ");
		double[] intArray = new double[strArray.length];
		boolean isNumData = true;

		try {
			for (int i = 0; i < strArray.length; i++) {
				intArray[i] = Integer.parseInt(strArray[i]);
			}
		} catch (NumberFormatException e) {
			isNumData = false;
		}

		return isNumData ? intArray : null;
	}		

	//データの標準化
	private static double[] normalize(double[] X){
		double[] res = new double[X.length];
		for(int i=0; i<X.length; i++){
			res[i] = (X[i] - Mean(X)) / Std(X);
		}
		return res;
	}
	
	//配列の標準偏差の計算
	private static double Std(double[] X){
		double var =0.0;
		double total=0.0;
		double lngt = X.length;
		double avg = Mean(X);
		for(int i=0; i<lngt; i++){
			total += Math.pow(X[i]-avg,2.0d);
		}
		var = total/lngt;
		return Math.sqrt(var);
	}
	
	//配列の平均の計算
	private static double Mean(double[] X){
		double sum = Sum(X);
		return sum/X.length;
	}
	
	//配列の和の計算
	private static double Sum(double[] X){
		double sum=0.0;
		for(int i=0; i<X.length; i++){
			sum += X[i];
		}
		return sum;
	}
	
	//List<Double> -> double[]への変換
	private static double[] ConvertDoubleArray(List<Double> list){
		double[] data = new double[list.size()];
		for(int i=0; i<list.size(); i++){
			data[i] = list.get(i);
		}
		return data;
	}
	
	private static double[] MergeArray(double[] array1, double[] array2){
		double[] mergeArray=new double[array1.length + array2.length];
	    System.arraycopy(array1, 0, mergeArray, 0, array1.length);
	    System.arraycopy(array2, 0, mergeArray, array1.length, array2.length);
	    return mergeArray;
	}

	//差分計算
	private static double[] Delta(double[] x, int k){
		double[] res = new double[x.length - k - 1];
		for(int i=k-1; i<x.length; i++){
			double tmp = x[i] - x[i-1];
			for(int j=0; j>k; j++){
				tmp -= x[i-j] - x[i-1-j];
			}
			res[i-k+1] = tmp;
		}
		return res;
	}

	//和分計算
	private static double[] Integration(double[] x, int k){
		double[] res = new double[x.length - k - 1];
		return res;
	}

	//一段目の変化点スコアの算出
	private static double[] Outlier(double[] X){
		int count = X.length - term - 1;
		double[][] trains = new double[count][term];
		double[] target = new double[count];
		
        double[] resid = new double[count];
        double[] mean = new double[count];
        double[] std = new double[count];
        //double[][] pred = new double[count][];
        double omega=0.0;
        double var=0.0;
        Map<String, double[]> map = new HashMap<String, double[]>();
        
        // term毎のtrainデータ配列を取得
        for(int i=0; i<count; i++){
        	for(int j=0; j<term; j++){
        		trains[i][j] = X[i+j];
        	}
        }
        
        //term毎のtargetデータの取得
        for(int t=0; t<count; t++){
        	target[t] = X[t + term + 1];
        }
        //fit = [ar.ARIMA(trains[t], self.order).fit(disp=0) for t in xrange(count)]
 
        // predict
        //resid = [fit[t].forecast(1)[0][0] - target[t] for t in xrange(count)]
        
        for(int t=0; t<count; t++){
        	omega = CalcOmega(trains[t]);
        	var = CalcVarhat(trains[t]);
        	map = Fit(trains[t], omega, var);
        	resid[t] = map.get("forecast")[0] - target[t];
        	//pred[t] = map.get("pred");
        	mean[t] = map.get("mean")[0];
        	std[t] = map.get("std")[0];
        }
        
        double[] scorePd = new double[resid.length];
        scorePd = logpdf(resid, mean, std);
        double[] score = new double[resid.length-(window-1)];
        score = smoothing(scorePd, window);
		
		return score;
	}

    private static double[] ChangePoint(double[] x){
        int count = x.length - term - 1;
		double[][] trains = new double[count][term];
		double[] target = new double[count];    
        double[] mean = new double[count];
        double[] std = new double[count];
		
	    // term毎のtrainデータ配列を取得
	    for(int i=0; i<count; i++){
	    	for(int j=0; j<term; j++){
	    		trains[i][j] = x[i+j];
	    	}
	    }
	    
	    //term毎のtargetデータの取得
	    for(int t=0; t<count; t++){
	    	target[t] = x[t + term + 1];
	    }
	    
	    for(int t=0; t<count; t++){
			mean[t] = Mean(trains[t]);
			std[t] = Std(trains[t]);	    	
	    }

        double[] scorePd = new double[target.length];
        scorePd = logpdf(target, mean, std);
        double[] score = new double[target.length-(window-1)];
        score = smoothing(scorePd, (int)Math.round(window*0.5));

        return score;
    }
	/*
	private double forecastArima(double[] X){
		ArimaModel arima = new ArimaModel(new double[]{1.0}, 5, new double[]{0.0});
		ArimaSim instance = new ArimaSim(new SimpleTimeSeries(X), arima, 1);
		return res;
	}
	*/
	/*
	private double CalcMu(double x, double mu){
		double newMu;
		newMu = (1-r)*mu + r*x;
		return newMu;
	}
	*/

	//モデルの当てはめと予測値の算出
	private static Map<String, double[]> Fit(double[] x, double omega, double var){
		double pred[] = new double[x.length];
		int seed = 555;
		pred[0] = x[0];
		double sigma = Math.sqrt(var);
		Map<String,double[]> res = new HashMap<String, double[]>();
		
		Random rand = new Random();
		rand.setSeed(seed);
		for(int i=1; i<x.length; i++){
			pred[i] = omega*x[i-1] + rand.nextGaussian()*sigma;
		}
		double[] mean = new double[] {Mean(pred)};
		double[] std = new double[] {Std(pred)};
		double[] forecast = new double[] {omega*x[x.length-1] + rand.nextGaussian()*sigma};
		//map.put("pred", pred);
		res.put("mean", mean);
		res.put("std", std);
		res.put("forecast", forecast);
		return res;
	}
	
	//yule-walker方程式を解く（omegaの推定）
	private static double CalcOmega(double[] x){
		double c1 = CalcC0(x);
		double c0 = CalcC1(x);
		double omega = c1/c0;
		return omega;
	}

	//shigma^2の推定
	private static double CalcVarhat(double[] x){
		double sum=0.0;
		for(int i=k; i<x.length; i++){
			sum += Math.pow(x[i] - x[i-1],2);
		}
		double varhat = sum/(x.length-k);
		return varhat;
	}	
	
	//自己共分散のc0の算出
	private static double CalcC0(double[] x){
		double sum=0.0;
		for(int i=k; i<x.length; i++){
			sum += x[i]*x[i];
		}
		double c0 = 1/(x.length - k)*sum;
		return c0;
	}

	//自己共分散のc1の算出
	private static double CalcC1(double[] x){
		double sum=0.0;
		for(int i=k; i<x.length; i++){
			sum += x[i]*x[i-1];
		}
		double c1 = sum/(x.length - k);
		return c1;
	}

	/*
	//xの推定
	private double CalcXhat(double omghat, double x_t1, double muhat){
		double xhat = omghat*(x_t1-muhat)+muhat;
		return xhat;
	}
	*/
	
	//確率(スコア)の計算
	private static double[] logpdf(double[] x, double[] mu, double[] std){
		int ln = x.length;
		double[] res = new double[ln];
		for(int i=0; i<ln; i++){
			double param = (x[i]-mu[i])/std[i];
			double kernel = Math.exp( -0.5*Math.pow(param,2) );
			res[i] = -1*Math.log( kernel/(Math.sqrt(2*Math.PI)*std[i]) );
		}
		return res;
	}

	//scoreの平滑化
	private static double[] smoothing(double[] x, int w){
		int ln = x.length;
		int i=0;
		double[] res = new double[ln-w+1];
		for(int t=w-1; t<ln; t++){
			double total = 0.0;
			for(int j=0; j<w; j++){
				total += x[t-j];
			}
			res[i] = total/w;
			i++;
		}
		return res;
	}
	
	//1回分のHouseholder変換
	private double[] Householder(double[] X){
		double norm;
		double weight;
		double u[] = new double[X.length];
		int i;
		
		norm = Math.sqrt(GetDotProduct(X, X));

		if(norm==0.0){
			if(X[0] < 0) norm = -norm;
			double Xd0 = X[0] + norm;

			weight = 1/(Math.sqrt(2*norm*Xd0));

			for(i=0; i<X.length; i++){
				if(i==0) u[i] =Xd0*weight; //uの算出
				else u[i] =X[i]*weight;
			}
		}
		
		return u;
	}
	
	//ベクトルの要素同士の掛け合わせ
	private double GetDotProduct(double[] vector1, double[] vector2){
		double sum = 0.0;

		if(vector1.length != vector2.length){
			throw new IllegalArgumentException("Cannot get dot product.");
		}

		for(int i=0; i<vector1.length; i++){
			sum += vector1[i] * vector2[i];
		}
		return sum;
	}
	
	//ベクトルのコピー
	private double[] VecCopy(double[] x){
		double[] copy = new double[x.length];
		for(int i=0; i<x.length; i++){
			copy[i] = x[i];
		}
		return copy;
	}

	//行列のコピー
	private double[][] MatCopy(double[][] x){
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
	
	//ファイル書き込み
	private static void WriteFile(double[] x){
        try{
            FileWriter fw = new FileWriter(PATH+"output/result.txt");                
            for(int i=0;i<x.length;i++){
                fw.write(x[i]+"\r\n");
            }
            fw.close();
       } catch(Exception e){
       }
	}	
}