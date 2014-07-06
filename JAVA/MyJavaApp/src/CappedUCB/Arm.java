package CappedUCB;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Arm {
	private double p; // Ÿ—˜Šm—¦
	private long X; //¡‚Ü‚Å‚Ì•ñV‚Ì‡Œv
	private long X2; //¡‚Ü‚Å‚Ì•ñV‚Ì2æ‚Ì‡Œv
	private int n; //‚±‚ê‚Ü‚Å‚Ì‘ƒvƒŒƒC‰ñ”
	private double price;
	private double max_price;
	
	private int BENEFIT; //•ñV‚Ì’l
	private final double GAP=0.99999998; // –Y‹pŒW” memory gap
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
	    if(p >= Math.random()){//“–‚½‚Á‚½ê‡
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	double pprice = Math.floor( this.price*suvRate() ); // ’ñˆÄ‰¿Ši
	    	res.put("BENEFIT", (double)this.BENEFIT);
	    	res.put("pprice", pprice);	    	
	    	return res;
	    }
    	double pprice = Math.floor( this.price*suvRate() ); // ’ñˆÄ‰¿Ši
    	res.put("BENEFIT", (double)0);
    	res.put("pprice", pprice);

	    return res; //ŠO‚ê‚½ê‡		
	}

	public Map<String, Double> vs(){
    	Map<String, Double> res = new HashMap<>();
    	long seed = System.currentTimeMillis();
    	Random rand = new Random(seed);
    	double cprice = rand.nextGaussian()*VAR+AVG;
    	
		this.n++;
	    if(this.price >= cprice){//“–‚½‚Á‚½ê‡
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	
	    	double pprice = 0.0;
	    	if(suvRate()<0.95){
	    		pprice = Math.floor( this.price*suvRate() ); // ’ñˆÄ‰¿Ši
	    	}else{
	    		pprice = Math.floor( this.price*0.85 );
	    	}
	    	res.put("BENEFIT", (double)this.BENEFIT);
	    	res.put("pprice", pprice);	    	
	    	return res;
	    }
    	double pprice = Math.floor( (this.max_price-this.price)*0.5 ); // ’ñˆÄ‰¿Ši
    	res.put("BENEFIT", (double)0.0);
    	res.put("pprice", pprice);
	    
	    return res; //ŠO‚ê‚½ê‡		
	}	
	
	// –Û”­¶‚Í‚ÉˆË‘¶
	public double UBC1(int t){
		return (double)(this.X)/(this.n) + Math.sqrt(2*Math.log((double)t)/this.n);
	}
	
	// ‚ÉŠÖŒW‚È‚­“–ŠY–Û‚ª¶‚¶‚éŠm—¦‚ª“™‚µ‚¢
	public double UBCpulas(int t){
		return (double)(this.X)/(this.n+Math.pow(10, -6)) + Math.sqrt( 1/(this.n+Math.pow(10, -6)) );
	}

	// ‚ÉŠÖŒW‚È‚­“–ŠY–Û‚ª¶‚¶‚éŠm—¦‚ª“™‚µ‚¢{–Y‹pŒW”•t‚«
	public double UBCpulasGap(int t){
		return (double)(this.X)/(this.n+Math.pow(10, -9))*Math.pow(this.GAP, this.n) 
				+ Math.sqrt( 1/(this.n+Math.pow(10, -9)) ) - 0.1*this.price/this.max_price ;
	}
	
	public double UBC1Tuned(int t){
		double aveX = (double)(this.X)/(this.n);
		double Vjs = (double)(this.X2)/(this.n) - aveX * aveX + Math.sqrt(2*Math.log((double)t)/this.n);
		return (double)(this.X)/(this.n) + Math.sqrt(Math.log((double)t)/this.n * Math.min(0.25, Vjs));
	}
	
	// «‚±‚±‚©‚ç“üD—p«
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
