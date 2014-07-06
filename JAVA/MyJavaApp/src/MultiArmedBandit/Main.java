package MultiArmedBandit;

import java.math.*;
import java.util.*;

public class Main {
	//“–‚½‚Á‚½ê‡‚Ì•ñV
	static int BENEFIT = 1; //¦C³
	static int ARM_NUM=10; //˜r‚Ì”
	static int MAX_STEP=10000;

	static int money = 0; //•ñVŠz‡Œv
	static int count = 0; //ƒQ[ƒ€ƒJƒEƒ“ƒg
	
	public static void main(String[] args){
		List<Arm> armlist = new ArrayList<>();
		// ˜r‚Ì¶¬
		for(int i=0; i<ARM_NUM; i++){
			armlist.add(new Arm(BENEFIT));
		}
		
		//˜r‚Ì‰Šú‰»(Še˜r1‰ñƒvƒŒƒC)
		initialize(armlist);
		
		// ‰^—p‚µ‚Â‚ÂÅ“K‚È˜r‚ğ’T‚·
		int evali = 0;
		for(int t=armlist.size(); t<=MAX_STEP; t++){    
			evali = explore(armlist, t);
		    //ƒvƒŒƒCŒã‚Ì•ñVŠz
		    if(t>=(int)(MAX_STEP*0.9999)) System.out.println( count+" "+money+"(played:"+evali+")" );
		    count++;
		}		
	}
	
	public static void initialize(List<Arm> arms){
		for(Arm arm: arms){
			money += arm.play(); //ƒvƒŒƒC‚·‚é
	
		    //ƒvƒŒƒCŒã‚Ì•ñVŠz
			arm.print(count);
			count++; 
		}		
	}
	
	public static int explore(List<Arm> arms, int t){
		int anum = 0;
	    double eval = -1.0;
	    int evali = -1;
	    //‚·‚×‚Ä‚Ìbandit‚Ì’†‚©‚ç•]‰¿’l‚Ìˆê”Ô‚‚¢‚à‚Ì‚ğ‘I‚Ô
	    for(Arm arm: arms){
	        double tmp = arm.UBCpulas(t); //UBC1Tuned
	        //System.out.println("arm="+anum+": tmp="+tmp);
	        if(eval < tmp){
	        	eval = tmp;
	        	evali = anum;
	        }
	        anum++;
	    }
	    //‚»‚Ìƒ}ƒVƒ“‚ğƒvƒŒƒC
	    money += arms.get(evali).play();	
		return evali;
	}
}
