package BehaviorAnalysis;

/****************************/
/*     関数値，微係数の計算 */
/****************************/
public class BFGSkansu {
	private int sw;
	private int num;
	private double[][] buy = null;
	private double[][] price = null;
	private double[][] disp = null;
//	private LogitModel LM;
					// コンストラクタ
	BFGSkansu (int s, int n, double[][] b, double[][] p, double[][] d) {
		this.sw = s; this.num=n;
		this.buy = b;
		this.price = p;
		this.disp = d;
//		LogitModel LM = obj;
	}
					// 与えられた点xから，dx方向へk*dxだけ進んだ
					// 点における関数値を計算する
	double snx(double k, double x[], double dx[]) // xが最大化したい係数
	{
		double x1, y1, z1, y = 0.0, w[] = new double [this.num];

		switch (this.sw) {
			case 1:
				w[0] = x[0] + k * dx[0];
				w[1] = x[1] + k * dx[1];
				x1   = w[0] - 1.0;
				y1   = w[1] - 2.0;
				y    = x1 * x1 + y1 * y1;
				break;
			case 2:
				w[0] = x[0] + k * dx[0];
				w[1] = x[1] + k * dx[1];
				x1   = w[1] - w[0] * w[0];
				y1   = 1.0 - w[0];
				y    = 100.0 * x1 * x1 + y1 * y1;
				break;
			case 3:
				w[0] = x[0] + k * dx[0];
				w[1] = x[1] + k * dx[1];
				x1   = 1.5 - w[0] * (1.0 - w[1]);
				y1   = 2.25 - w[0] * (1.0 - w[1] * w[1]);
				z1   = 2.625 - w[0] * (1.0 - w[1] * w[1] * w[1]);
				y    = x1 * x1 + y1 * y1 + z1 * z1;
				break;
			case 4:
				for(int i=0; i<this.num; i++){
					//System.out.println("dx= "+dx[i]);
					w[i] = x[i] + k*dx[i]; // dxは最大化問題を最小化問題にしているため施したものを使用
				}
				y = -1*LogitModel.calcLogLKH(w, this.price, this.disp, this.buy); //上記同様-1
				//System.out.println("y= "+y);
				//ShowData.showVec(w);
				break;
		}
		return y;
	}
					// 関数の微分
	double[] dsnx(double x[], double dx[])
	{
		switch (sw) {
			case 1:
				dx[0] = 2.0 * (x[0] - 1.0);
				dx[1] = 2.0 * (x[1] - 2.0);
				break;
			case 2:
				dx[0] = -400.0 * x[0] * (x[1] - x[0] * x[0]) - 2.0 * (1.0 - x[0]);
				dx[1] = 200.0 * (x[1] - x[0] * x[0]);
				break;
			case 3:
				dx[0] = -2.0 * (1.0 - x[1]) * (1.5 - x[0] * (1.0 - x[1])) -
                        2.0 * (1.0 - x[1] * x[1]) * (2.25 - x[0] * (1.0 - x[1] * x[1])) -
                        2.0 * (1.0 - x[1] * x[1] * x[1]) * (2.625 - x[0] * (1.0 - x[1] * x[1] * x[1]));
				dx[1] = 2.0 * x[0] * (1.5 - x[0] * (1.0 - x[1])) +
                        4.0 * x[0] * x[1] * (2.25 - x[0] * (1.0 - x[1] * x[1])) +
                        6.0 * x[0] * x[1] * x[1] * (2.625 - x[0] * (1.0 - x[1] * x[1] * x[1]));
				break;
			case 4:
				dx = LinearAlgebra.cnstMultVec( -1, 
						LogitModel.calcGradient(4, 3, x, this.price, this.disp, this.buy) );
				//ShowData.showVec(dx);
				break;
		}
		return dx;
	}
}