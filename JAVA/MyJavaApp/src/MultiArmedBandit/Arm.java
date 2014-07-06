package MultiArmedBandit;

public class Arm {
	double p; //当たる確率
	long X; //今までの報酬の合計
	long X2; //今までの報酬の2乗の合計
	int n; //これまでの総プレイ回数
	int BENEFIT; //報酬の値
	
	public Arm(int BENEFIT){
		this.BENEFIT = BENEFIT;
	    while(true){
	    	this.p = Math.random();
		      if(this.p<0.4) break;
	    }		  
	}
	
	public int play(){
	    this.n++;
	    if(p >= Math.random()){//当たった場合
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	return this.BENEFIT;
	    }
	    return 0; //外れた場合		
	}

	// 事象発生は時刻に依存
	public double UBC1(int t){
		return (double)(this.X)/(this.n) + Math.sqrt(2*Math.log((double)t)/this.n);
	}
	
	// 時刻に関係なく当該事象が生じる確率が等しい
	public double UBCpulas(int t){
		return (double)(this.X)/(this.n) + Math.sqrt(1/this.n);
	}

	public double UBC1Tuned(int t){
		double aveX = (double)(this.X)/(this.n);
		double Vjs = (double)(this.X2)/(this.n) - aveX * aveX + Math.sqrt(2*Math.log((double)t)/this.n);
		return (double)(this.X)/(this.n) + Math.sqrt(Math.log((double)t)/this.n * Math.min(0.25, Vjs));
	}
	
	public void print(int anum){
		System.out.println("arm"+anum+": p="+this.p);
	}
}
