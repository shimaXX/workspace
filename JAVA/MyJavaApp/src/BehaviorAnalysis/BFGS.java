package BehaviorAnalysis;

/****************************
/*     科学技術系算用の手法 */
/****************************/
public class BFGS {

	/************************************************************/
	/*     DFP法 or BFGS法                                      */
	/*          method : =0 : DFP法                             */
	/*                   =1 : BFGS法                            */
	/*          opt_1 : =0 : １次元最適化を行わない             */
	/*                  =1 : １次元最適化を行う                 */
	/*          max : 最大繰り返し回数                          */
	/*          n : 次元                                        */
	/*          eps : 収束判定条件                              */
	/*          step : きざみ幅                                 */
	/*          y : 最小値                                      */
	/*          x1 : x(初期値と答え)                            */
	/*          dx : 関数の微分値                               */
	/*          H : Hesse行列の逆行列                           */
	/*          kn : 関数値，微係数を計算するクラスオブジェクト */
	/*          return : >=0 : 正常終了(収束回数)               */
	/*                   =-1 : 収束せず                         */
	/*                   =-2 : １次元最適化の区間が求まらない   */
	/*                   =-3 : 黄金分割法が失敗                 */
	/************************************************************/
	/*
		// 関数 a，DFP法，一次元最適化を使用しない
	関数 1 変数の数 2 最大試行回数 100 一次元最適化 0
	方法 0 許容誤差 1.0e-10 刻み幅 0.5
	初期値 0.0 0.0
		// 関数 a，DFP法，一次元最適化を使用する
	関数 1 変数の数 2 最大試行回数 100 一次元最適化 1
	方法 0 許容誤差 1.0e-10 刻み幅 0.5
	初期値 0.0 0.0
		// 関数 a，BFGS法，一次元最適化を使用しない
	関数 1 変数の数 2 最大試行回数 100 一次元最適化 0
	方法 1 許容誤差 1.0e-10 刻み幅 0.5
	初期値 0.0 0.0
		// 関数 a，BFGS法，一次元最適化を使用する
	関数 1 変数の数 2 最大試行回数 100 一次元最適化 1
	方法 1 許容誤差 1.0e-10 刻み幅 0.5
	初期値 0.0 0.0
		// 関数 b，DFP法，一次元最適化を使用しない
	関数 2 変数の数 2 最大試行回数 100 一次元最適化 0
	方法 0 許容誤差 1.0e-10 刻み幅 0.2
	初期値 0.0 0.0
		// 関数 b，DFP法，一次元最適化を使用する
	関数 2 変数の数 2 最大試行回数 100 一次元最適化 1
	方法 0 許容誤差 1.0e-10 刻み幅 0.1
	初期値 0.0 0.0
		// 関数 b，BFGS法，一次元最適化を使用しない
	関数 2 変数の数 2 最大試行回数 1000 一次元最適化 0
	方法 1 許容誤差 1.0e-10 刻み幅 0.02
	初期値 0.0 0.0
		// 関数 b，BFGS法，一次元最適化を使用する
	関数 2 変数の数 2 最大試行回数 100 一次元最適化 1
	方法 1 許容誤差 1.0e-10 刻み幅 0.002
	初期値 0.0 0.0
		// 関数 c，DFP法，一次元最適化を使用しない
	関数 3 変数の数 2 最大試行回数 200 一次元最適化 0
	方法 0 許容誤差 1.0e-10 刻み幅 0.1
	初期値 0.0 0.0
		// 関数 c，DFP法，一次元最適化を使用する
	関数 3 変数の数 2 最大試行回数 100 一次元最適化 1
	方法 0 許容誤差 1.0e-10 刻み幅 0.1
	初期値 0.0 0.0
		// 関数 c，BFGS法，一次元最適化を使用しない
	関数 3 変数の数 2 最大試行回数 200 一次元最適化 0
	方法 1 許容誤差 1.0e-10 刻み幅 0.09
	初期値 0.0 0.0
		// 関数 c，BFGS法，一次元最適化を使用する
	関数 3 変数の数 2 最大試行回数 200 一次元最適化 1
	方法 1 許容誤差 1.0e-10 刻み幅 0.09
	初期値 0.0 0.0
	*/
	static int DFP_BFGS(int method, int opt_1, int max, int n, double eps, double step, double y[],
                        double x1[], double dx[], double H[][], BFGSkansu kn)
	{
		double f1, f2, g[], g1[], g2[], H1[][], H2[][], I[][], k, s[], sm, sm1, sm2,
               sp, w[], x2[], y1[] = new double [1], y2[] = new double [1];
		int count = 0, i1, i2, i3, sw = 0, sw1[] = new int [1];

		x2 = new double [n];
		g  = new double [n];
		g1 = new double [n];
		g2 = new double [n];
		s  = new double [n];
		w  = new double [n];

		y1[0] = kn.snx(0.0, x1, dx);
		g1 = kn.dsnx(x1, g1);
		
		H1 = new double [n][n];
		H2 = new double [n][n];
		I  = new double [n][n];
		for (i1 = 0; i1 < n; i1++) {
			for (i2 = 0; i2 < n; i2++) {
				H[i1][i2] = 0.0;
				I[i1][i2] = 0.0;
			}
			H[i1][i1] = 1.0;
			I[i1][i1] = 1.0;
		}

		while (count < max && sw == 0) {
			count++;
					// 方向の計算
			for (i1 = 0; i1 < n; i1++) {
				dx[i1] = 0.0;
				for (i2 = 0; i2 < n; i2++)
					dx[i1] -= H[i1][i2] * g1[i2];
			}
					// １次元最適化を行わない
			if (opt_1 == 0) {
						// 新しい点
				for (i1 = 0; i1 < n; i1++)
					x2[i1] = x1[i1] + step * dx[i1];
						// 新しい関数値
				y2[0] = kn.snx(0.0, x2, dx);
			}
					// １次元最適化を行う
			else {
						// 区間を決める
				sw1[0] = 0;
				f1     = y1[0];
				sp     = step;
				f2     = kn.snx(sp, x1, dx);
				System.out.println("f1= "+f1);
				System.out.println("f21= "+f2);
				if (f2 > f1)
					sp = -step;
				for (i1 = 0; i1 < max && sw1[0] == 0; i1++) {
					f2 = kn.snx(sp, x1, dx);
					System.out.println("f22= "+f2);
					if (f2 > f1)
						sw1[0] = 1;
					else {
						sp *= 2.0;
						f1  = f2;
					}
				}
						// 区間が求まらない
				if (sw1[0] == 0)
					sw = -2;
						// 区間が求まった
				else {
							// 黄金分割法
					k = BFGS.gold(0.0, sp, eps, y2, sw1, max, x1, dx, kn);
							// 黄金分割法が失敗
					if (sw1[0] < 0)
						sw = -3;
							// 黄金分割法が成功
					else {
								// 新しい点
						for (i1 = 0; i1 < n; i1++)
							x2[i1] = x1[i1] + k * dx[i1];
					}
				}
			}

			if (sw == 0) {
					// 収束（関数値の変化＜ｅｐｓ）
				if (Math.abs(y2[0]-y1[0]) < eps) {
					sw   = count;
					y[0] = y2[0];
					for (i1 = 0; i1 < n; i1++)
						x1[i1] = x2[i1];
				}
					// 関数値の変化が大きい
				else {
						// 傾きの計算
					g2 = kn.dsnx(x2, g2);
					sm = 0.0;
					for (i1 = 0; i1 < n; i1++)
						sm += g2[i1] * g2[i1];
					sm = Math.sqrt(sm);
						// 収束（傾き＜ｅｐｓ）　傾きが0に近くなれば収束
					if (sm < eps) {
						sw   = count; // 繰り返しの回数
						y[0] = y2[0]; // 今の尤度
						for (i1 = 0; i1 < n; i1++)
							x1[i1] = x2[i1];
					}
						// 収束していない
					else {
						for (i1 = 0; i1 < n; i1++) {
							g[i1] = g2[i1] - g1[i1];
							s[i1] = x2[i1] - x1[i1];
						}
						sm1 = 0.0;
						for (i1 = 0; i1 < n; i1++)
							sm1 += s[i1] * g[i1];
							// DFP法
						if (method == 0) {
							for (i1 = 0; i1 < n; i1++) {
								w[i1] = 0.0;
								for (i2 = 0; i2 < n; i2++)
									w[i1] += g[i2] * H[i2][i1];
							}
							sm2 = 0.0;
							for (i1 = 0; i1 < n; i1++)
								sm2 += w[i1] * g[i1];
							for (i1 = 0; i1 < n; i1++) {
								w[i1] = 0.0;
								for (i2 = 0; i2 < n; i2++)
									w[i1] += H[i1][i2] * g[i2];
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++)
									H1[i1][i2] = w[i1] * g[i2];
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++) {
									H2[i1][i2] = 0.0;
									for (i3 = 0; i3 < n; i3++)
										H2[i1][i2] += H1[i1][i3] * H[i3][i2];
								}
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++)
									H[i1][i2] = H[i1][i2]  + s[i1] * s[i2] / sm1 - H2[i1][i2] / sm2;
							}
						}
							// BFGS法
						else {
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++)
									H1[i1][i2] = I[i1][i2] - s[i1] * g[i2] / sm1;
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++) {
									H2[i1][i2] = 0.0;
									for (i3 = 0; i3 < n; i3++)
										H2[i1][i2] += H1[i1][i3] * H[i3][i2];
								}
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++) {
									H[i1][i2] = 0.0;
									for (i3 = 0; i3 < n; i3++)
										H[i1][i2] += H2[i1][i3] * H1[i3][i2];
								}
							}
							for (i1 = 0; i1 < n; i1++) {
								for (i2 = 0; i2 < n; i2++)
									H[i1][i2] += s[i1] * s[i2] / sm1;
							}
						}
						y1[0] = y2[0];
						for (i1 = 0; i1 < n; i1++) {
							g1[i1] = g2[i1];
							x1[i1] = x2[i1];
						}
					}
				}
			}
		}

		if (sw == 0)
			sw = -1;

		return sw;
	}

	/********************************************************************/
	/*     黄金分割法(与えられた方向での最小値)                         */
	/*          a,b : 初期区間 a < b                                    */
	/*          eps : 許容誤差                                          */
	/*          val : 関数値                                            */
	/*          ind : 計算状況                                          */
	/*                  >= 0 : 正常終了(収束回数)                       */
	/*                  = -1 : 収束せず                                 */
	/*          max : 最大試行回数                                      */
	/*          w : 位置                                                */
	/*          dw : 傾きの成分                                         */
	/*          kn : 関数値を計算するクラスオブジェクト */
	/*          return : 結果(w＋y＊dwのy)                              */
	/********************************************************************/
	static double gold(double a, double b, double eps, double val[], int ind[], int max,
                       double w[], double dw[], BFGSkansu kn)
	{
		double f1, f2, fa, fb, tau = (Math.sqrt(5.0) - 1.0) / 2.0, x = 0.0, x1, x2;
		int count = 0;
					// 初期設定
		ind[0] = -1;
		x1     = b - tau * (b - a);
		x2     = a + tau * (b - a);
		f1     = kn.snx(x1, w, dw);
		f2     = kn.snx(x2, w, dw);
					// 計算
		while (count < max && ind[0] < 0) {
			count += 1;
			if (f2 > f1) {
				if (Math.abs(b-a) < eps) {
					ind[0] = 0;
					x      = x1;
					val[0] = f1;
				}
				else {
					b  = x2;
					x2 = x1;
					x1 = a + (1.0 - tau) * (b - a);
					f2 = f1;
					f1 = kn.snx(x1, w, dw);
				}
			}
			else {
				if (Math.abs(b-a) < eps) {
					ind[0] = 0;
					x      = x2;
					val[0] = f2;
					f1     = f2;
				}
				else {
					a  = x1;
					x1 = x2;
					x2 = b - (1.0 - tau) * (b - a);
					f1 = f2;
					f2 = kn.snx(x2, w, dw);
				}
			}
		}
					// 収束した場合の処理
		if (ind[0] == 0) {
			ind[0] = count;
			fa     = kn.snx(a, w, dw);
			fb     = kn.snx(b, w, dw);
			if (fb < fa) {
				a  = b;
				fa = fb;
			}
			if (fa < f1) {
				x      = a;
				val[0] = fa;
			}
		}

		return x;
	}
}