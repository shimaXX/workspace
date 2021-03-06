package MultiArmedBandit;

import java.math.*;
import java.util.*;

public class Main {
	//当たった場合の報酬
	static int BENEFIT = 1; //※修正
	static int ARM_NUM=10; //腕の数
	static int MAX_STEP=10000;

	static int money = 0; //報酬額合計
	static int count = 0; //ゲームカウント
	
	public static void main(String[] args){
		List<Arm> armlist = new ArrayList<>();
		// 腕の生成
		for(int i=0; i<ARM_NUM; i++){
			armlist.add(new Arm(BENEFIT));
		}
		
		//腕の初期化(各腕1回プレイ)
		initialize(armlist);
		
		// 運用しつつ最適な腕を探す
		int evali = 0;
		for(int t=armlist.size(); t<=MAX_STEP; t++){    
			evali = explore(armlist, t);
		    //プレイ後の報酬額
		    if(t>=(int)(MAX_STEP*0.9999)) System.out.println( count+" "+money+"(played:"+evali+")" );
		    count++;
		}		
	}
	
	public static void initialize(List<Arm> arms){
		for(Arm arm: arms){
			money += arm.play(); //プレイする
	
		    //プレイ後の報酬額
			arm.print(count);
			count++; 
		}		
	}
	
	public static int explore(List<Arm> arms, int t){
		int anum = 0;
	    double eval = -1.0;
	    int evali = -1;
	    //すべてのbanditの中から評価値の一番高いものを選ぶ
	    for(Arm arm: arms){
	        double tmp = arm.UBCpulas(t); //UBC1Tuned
	        //System.out.println("arm="+anum+": tmp="+tmp);
	        if(eval < tmp){
	        	eval = tmp;
	        	evali = anum;
	        }
	        anum++;
	    }
	    //そのマシンをプレイ
	    money += arms.get(evali).play();	
		return evali;
	}
}
