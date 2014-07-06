package MultiArmedBandit;

import java.math.*;
import java.util.*;

public class Main {
	//���������ꍇ�̕�V
	static int BENEFIT = 1; //���C��
	static int ARM_NUM=10; //�r�̐�
	static int MAX_STEP=10000;

	static int money = 0; //��V�z���v
	static int count = 0; //�Q�[���J�E���g
	
	public static void main(String[] args){
		List<Arm> armlist = new ArrayList<>();
		// �r�̐���
		for(int i=0; i<ARM_NUM; i++){
			armlist.add(new Arm(BENEFIT));
		}
		
		//�r�̏�����(�e�r1��v���C)
		initialize(armlist);
		
		// �^�p���œK�Șr��T��
		int evali = 0;
		for(int t=armlist.size(); t<=MAX_STEP; t++){    
			evali = explore(armlist, t);
		    //�v���C��̕�V�z
		    if(t>=(int)(MAX_STEP*0.9999)) System.out.println( count+" "+money+"(played:"+evali+")" );
		    count++;
		}		
	}
	
	public static void initialize(List<Arm> arms){
		for(Arm arm: arms){
			money += arm.play(); //�v���C����
	
		    //�v���C��̕�V�z
			arm.print(count);
			count++; 
		}		
	}
	
	public static int explore(List<Arm> arms, int t){
		int anum = 0;
	    double eval = -1.0;
	    int evali = -1;
	    //���ׂĂ�bandit�̒�����]���l�̈�ԍ������̂�I��
	    for(Arm arm: arms){
	        double tmp = arm.UBCpulas(t); //UBC1Tuned
	        //System.out.println("arm="+anum+": tmp="+tmp);
	        if(eval < tmp){
	        	eval = tmp;
	        	evali = anum;
	        }
	        anum++;
	    }
	    //���̃}�V�����v���C
	    money += arms.get(evali).play();	
		return evali;
	}
}
