package MultiArmedBandit;

public class Arm {
	double p; //������m��
	long X; //���܂ł̕�V�̍��v
	long X2; //���܂ł̕�V��2��̍��v
	int n; //����܂ł̑��v���C��
	int BENEFIT; //��V�̒l
	
	public Arm(int BENEFIT){
		this.BENEFIT = BENEFIT;
	    while(true){
	    	this.p = Math.random();
		      if(this.p<0.4) break;
	    }		  
	}
	
	public int play(){
	    this.n++;
	    if(p >= Math.random()){//���������ꍇ
	    	this.X += this.BENEFIT;
	    	this.X2 += this.BENEFIT * this.BENEFIT;
	    	return this.BENEFIT;
	    }
	    return 0; //�O�ꂽ�ꍇ		
	}

	// ���۔����͎����Ɉˑ�
	public double UBC1(int t){
		return (double)(this.X)/(this.n) + Math.sqrt(2*Math.log((double)t)/this.n);
	}
	
	// �����Ɋ֌W�Ȃ����Y���ۂ�������m����������
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
