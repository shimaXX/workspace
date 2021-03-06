package CappedUCB;

import java.math.*;
import java.util.*;
import java.util.Map.Entry;

public class Main {
	//当たった場合の報酬
	static int BENEFIT = 1; //※修正
	static int ARM_NUM=10; //腕の数
	static int MAX_STEP=1000000;
	static int PRICE_CAP=50;
	static int MIN = 100; // 入札勝利数の下限
	
	static int money = 0; //報酬額合計
	static int count = 0; //ゲームカウント
	
	static int avg=20;
	
	public static void main(String[] args){
		
		// 運用しつつ最適な腕を探す
		double bprice = 0.0; // best price
		Map<Double, Arm> armmap = new HashMap<>();
		double nprice = 0.0; // 提案される価格
		for(int t=0; t<MAX_STEP; t++){
			if(t>=100000) PRICE_CAP=100; avg=35; //予算上限変更に対するロバスト性チェック
			if(money<=MIN){
				double price = culcPrice()*PRICE_CAP;
				//double price = culcPrice();
				if(!armmap.containsKey(price)){
					armmap.put(price, new Arm(BENEFIT, price, PRICE_CAP, avg));
					money +=armmap.get(price).vs().get("BENEFIT");
					
				}else{
					bprice = explore(armmap, t).get("price");
				}
			}else{
				Map<String, Double> res = explore(armmap, t);
				bprice = res.get("price");
				nprice = res.get("pprice");
				if(!armmap.containsKey(nprice) && nprice != 0.0){				
					armmap.put(nprice, new Arm(BENEFIT, nprice, PRICE_CAP, avg));
				}
			}
		    //プレイ後の報酬額
			//if(count%100 == 0 ) System.out.println( count+" "+money+"(played:"+bprice+")" );
			if(count%100 == 0 ) System.out.println( bprice );
			
		    count++;
		}
		
		for(Entry<Double, Arm> e:armmap.entrySet()){
			e.getValue().print(e.getKey().intValue());
		}
		
	}
		
	public static Map<String, Double> explore(Map<Double,Arm> arms, int t){
	    double eval = -1.0;
	    double evali = -1;
	    Map<String, Double> res = new HashMap<>();
	    //すべてのbanditの中から評価値の一番高いものを選ぶ
	    for(Entry<Double, Arm> e: arms.entrySet()){
	        double tmp = e.getValue().UBCpulasGap(t); //UBC1Tuned(t) index UBCpulas(t)
	        //System.out.println("arm="+anum+": tmp="+tmp);
	        if(eval < tmp){
	        	eval = tmp;
	        	evali = e.getKey();
	        }
	    }
	    //そのマシンをプレイ
	    money += arms.get(evali).vs().get("BENEFIT");
	    double pprice = arms.get(evali).vs().get("pprice");
	    res.put("price", evali);
	    res.put("pprice", pprice); // 提案価格
		return res;
	}
	
	//計算怪しい(?).要見直し
	public static double culcPrice(){
		double delta = Math.pow(( 1/(money+Math.pow(10, -6))+Math.pow(10,-6) * Math.log(money+Math.pow(10, -6))), 0.25);
		double eps = Math.pow(money+Math.pow(10, -6), -0.25);
		double alph = Math.pow((double)money/(count+Math.pow(10, -6)), 1-delta);
		double gamma = Math.min( alph, Math.pow(Math.exp(1), -1) );
		double m=0;
		
		int l=0; double Rmax=0; double Rl=0;
		double pl=0; double Sl=0; double plmax=0;

		do{
			pl = Math.pow(1+delta, -l);
			m=delta*count/Math.log(1/eps)*Math.log(1+delta);
			
			//Sl = Math.exp(-pl); // ここはあってるかわからない
			Sl = Math.exp(m); // ここはあってるかわからない
			//Rl=pl*m/Math.exp(1);
			Rl=pl*Sl;
			
			if( Sl>=Math.pow(1+delta, -1)*gamma && Rl>=Rmax ){
				Rmax=Rl; plmax=pl;
			}
			l++;
		}while(pl>eps && Sl<(1+gamma)*alph && Rl>Math.pow(1+gamma, -2)*Rmax);
		//System.out.println("plmax="+plmax);
		return plmax;
	}
}
