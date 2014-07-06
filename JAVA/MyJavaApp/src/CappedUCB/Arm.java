package CappedUCB;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Arm {
	private double p; // �����m��
	private long X; //���܂ł̕�V�̍��v
	private long X2; //���܂ł̕�V��2��̍��v
	private int n; //����܂ł̑��v���C��
	private double price;
	private double max_price;
	
	private int BENEFIT; //��V�̒l
	private final double GAP=0.99999998; // �Y�p�W�� memory gap
	private final double VAR=5;
	private double AVG;	
	
	public Arm(int BENEFIT, double price, double max_price, double avg){
		this.BENEFIT = BENEFIT;
	    while(true){
	    	this.p = Math.random();
		      if(this.p<0.4) break;
	    }
	    this.price=price;
	    this.max_price = max_price;
	    this.AVG = avg;
	}
	
	public Map<String, Double> play(){
    	Map<String, Double> res = new HashMap<>();

		this.n++;
	    if(p >= Math.random()){//���������ꍇ
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	double pprice = Math.floor( this.price*suvRate() ); // ��ĉ��i
	    	res.put("BENEFIT", (double)this.BENEFIT);
	    	res.put("pprice", pprice);	    	
	    	return res;
	    }
    	double pprice = Math.floor( this.price*suvRate() ); // ��ĉ��i
    	res.put("BENEFIT", (double)0);
    	res.put("pprice", pprice);

	    return res; //�O�ꂽ�ꍇ		
	}

	public Map<String, Double> vs(){
    	Map<String, Double> res = new HashMap<>();
    	long seed = System.currentTimeMillis();
    	Random rand = new Random(seed);
    	double cprice = rand.nextGaussian()*VAR+AVG;
    	
		this.n++;
	    if(this.price >= cprice){//���������ꍇ
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	
	    	double pprice = 0.0;
	    	if(suvRate()<0.95){
	    		pprice = Math.floor( this.price*suvRate() ); // ��ĉ��i
	    	}else{
	    		pprice = Math.floor( this.price*0.85 );
	    	}
	    	res.put("BENEFIT", (double)this.BENEFIT);
	    	res.put("pprice", pprice);	    	
	    	return res;
	    }
    	double pprice = Math.floor( (this.max_price-this.price)*0.5 ); // ��ĉ��i
    	res.put("BENEFIT", (double)0.0);
    	res.put("pprice", pprice);
	    
	    return res; //�O�ꂽ�ꍇ		
	}	
	
	// ���۔����͎����Ɉˑ�
	public double UBC1(int t){
		return (double)(this.X)/(this.n) + Math.sqrt(2*Math.log((double)t)/this.n);
	}
	
	// �����Ɋ֌W�Ȃ����Y���ۂ�������m����������
	public double UBCpulas(int t){
		return (double)(this.X)/(this.n+Math.pow(10, -6)) + Math.sqrt( 1/(this.n+Math.pow(10, -6)) );
	}

	// �����Ɋ֌W�Ȃ����Y���ۂ�������m�����������{�Y�p�W���t��
	public double UBCpulasGap(int t){
		return (double)(this.X)/(this.n+Math.pow(10, -9))*Math.pow(this.GAP, this.n) 
				+ Math.sqrt( 1/(this.n+Math.pow(10, -9)) ) - 0.1*this.price/this.max_price ;
	}
	
	public double UBC1Tuned(int t){
		double aveX = (double)(this.X)/(this.n);
		double Vjs = (double)(this.X2)/(this.n) - aveX * aveX + Math.sqrt(2*Math.log((double)t)/this.n);
		return (double)(this.X)/(this.n) + Math.sqrt(Math.log((double)t)/this.n * Math.min(0.25, Vjs));
	}
	
	// ������������D�p��
	public double index(){ // total revenue
		return this.price*Math.min( this.X, this.n*(suvRate()+confRad()) );
	}
	
	public double confRad(){ //culcConfidenceRadius
		double alph = Math.log(this.n+Math.pow(10, -6));
		double denom = 1/(this.n+1);
		return alph*denom + Math.pow(alph*suvRate()*denom, 0.5);
	}
	
	public double suvRate(){ //survival rate
		return (double)(this.X/(this.n+Math.pow(10, -6)) );
	}
	
	public void print(int anum){
		System.out.println("arm"+anum+": win_rate="+(double)this.X/this.n);
	}	
}
