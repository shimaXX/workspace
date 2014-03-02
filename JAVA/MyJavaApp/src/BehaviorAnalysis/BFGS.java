package BehaviorAnalysis;

/****************************
/*     �Ȋw�Z�p�n�Z�p�̎�@ */
/****************************/
public class BFGS {

	/************************************************************/
	/*     DFP�@ or BFGS�@                                      */
	/*          method : =0 : DFP�@                             */
	/*                   =1 : BFGS�@                            */
	/*          opt_1 : =0 : �P�����œK�����s��Ȃ�             */
	/*                  =1 : �P�����œK�����s��                 */
	/*          max : �ő�J��Ԃ���                          */
	/*          n : ����                                        */
	/*          eps : �����������                              */
	/*          step : �����ݕ�                                 */
	/*          y : �ŏ��l                                      */
	/*          x1 : x(�����l�Ɠ���)                            */
	/*          dx : �֐��̔����l                               */
	/*          H : Hesse�s��̋t�s��                           */
	/*          kn : �֐��l�C���W�����v�Z����N���X�I�u�W�F�N�g */
	/*          return : >=0 : ����I��(������)               */
	/*                   =-1 : ��������                         */
	/*                   =-2 : �P�����œK���̋�Ԃ����܂�Ȃ�   */
	/*                   =-3 : ���������@�����s                 */
	/************************************************************/
	/*
		// �֐� a�CDFP�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 1 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 0
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.5
	�����l 0.0 0.0
		// �֐� a�CDFP�@�C�ꎟ���œK�����g�p����
	�֐� 1 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 1
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.5
	�����l 0.0 0.0
		// �֐� a�CBFGS�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 1 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 0
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.5
	�����l 0.0 0.0
		// �֐� a�CBFGS�@�C�ꎟ���œK�����g�p����
	�֐� 1 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 1
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.5
	�����l 0.0 0.0
		// �֐� b�CDFP�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 2 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 0
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.2
	�����l 0.0 0.0
		// �֐� b�CDFP�@�C�ꎟ���œK�����g�p����
	�֐� 2 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 1
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.1
	�����l 0.0 0.0
		// �֐� b�CBFGS�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 2 �ϐ��̐� 2 �ő厎�s�� 1000 �ꎟ���œK�� 0
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.02
	�����l 0.0 0.0
		// �֐� b�CBFGS�@�C�ꎟ���œK�����g�p����
	�֐� 2 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 1
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.002
	�����l 0.0 0.0
		// �֐� c�CDFP�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 3 �ϐ��̐� 2 �ő厎�s�� 200 �ꎟ���œK�� 0
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.1
	�����l 0.0 0.0
		// �֐� c�CDFP�@�C�ꎟ���œK�����g�p����
	�֐� 3 �ϐ��̐� 2 �ő厎�s�� 100 �ꎟ���œK�� 1
	���@ 0 ���e�덷 1.0e-10 ���ݕ� 0.1
	�����l 0.0 0.0
		// �֐� c�CBFGS�@�C�ꎟ���œK�����g�p���Ȃ�
	�֐� 3 �ϐ��̐� 2 �ő厎�s�� 200 �ꎟ���œK�� 0
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.09
	�����l 0.0 0.0
		// �֐� c�CBFGS�@�C�ꎟ���œK�����g�p����
	�֐� 3 �ϐ��̐� 2 �ő厎�s�� 200 �ꎟ���œK�� 1
	���@ 1 ���e�덷 1.0e-10 ���ݕ� 0.09
	�����l 0.0 0.0
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
					// �����̌v�Z
			for (i1 = 0; i1 < n; i1++) {
				dx[i1] = 0.0;
				for (i2 = 0; i2 < n; i2++)
					dx[i1] -= H[i1][i2] * g1[i2];
			}
					// �P�����œK�����s��Ȃ�
			if (opt_1 == 0) {
						// �V�����_
				for (i1 = 0; i1 < n; i1++)
					x2[i1] = x1[i1] + step * dx[i1];
						// �V�����֐��l
				y2[0] = kn.snx(0.0, x2, dx);
			}
					// �P�����œK�����s��
			else {
						// ��Ԃ����߂�
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
						// ��Ԃ����܂�Ȃ�
				if (sw1[0] == 0)
					sw = -2;
						// ��Ԃ����܂���
				else {
							// ���������@
					k = BFGS.gold(0.0, sp, eps, y2, sw1, max, x1, dx, kn);
							// ���������@�����s
					if (sw1[0] < 0)
						sw = -3;
							// ���������@������
					else {
								// �V�����_
						for (i1 = 0; i1 < n; i1++)
							x2[i1] = x1[i1] + k * dx[i1];
					}
				}
			}

			if (sw == 0) {
					// �����i�֐��l�̕ω����������j
				if (Math.abs(y2[0]-y1[0]) < eps) {
					sw   = count;
					y[0] = y2[0];
					for (i1 = 0; i1 < n; i1++)
						x1[i1] = x2[i1];
				}
					// �֐��l�̕ω����傫��
				else {
						// �X���̌v�Z
					g2 = kn.dsnx(x2, g2);
					sm = 0.0;
					for (i1 = 0; i1 < n; i1++)
						sm += g2[i1] * g2[i1];
					sm = Math.sqrt(sm);
						// �����i�X�����������j�@�X����0�ɋ߂��Ȃ�Ύ���
					if (sm < eps) {
						sw   = count; // �J��Ԃ��̉�
						y[0] = y2[0]; // ���̖ޓx
						for (i1 = 0; i1 < n; i1++)
							x1[i1] = x2[i1];
					}
						// �������Ă��Ȃ�
					else {
						for (i1 = 0; i1 < n; i1++) {
							g[i1] = g2[i1] - g1[i1];
							s[i1] = x2[i1] - x1[i1];
						}
						sm1 = 0.0;
						for (i1 = 0; i1 < n; i1++)
							sm1 += s[i1] * g[i1];
							// DFP�@
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
							// BFGS�@
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
	/*     ���������@(�^����ꂽ�����ł̍ŏ��l)                         */
	/*          a,b : ������� a < b                                    */
	/*          eps : ���e�덷                                          */
	/*          val : �֐��l                                            */
	/*          ind : �v�Z��                                          */
	/*                  >= 0 : ����I��(������)                       */
	/*                  = -1 : ��������                                 */
	/*          max : �ő厎�s��                                      */
	/*          w : �ʒu                                                */
	/*          dw : �X���̐���                                         */
	/*          kn : �֐��l���v�Z����N���X�I�u�W�F�N�g */
	/*          return : ����(w�{y��dw��y)                              */
	/********************************************************************/
	static double gold(double a, double b, double eps, double val[], int ind[], int max,
                       double w[], double dw[], BFGSkansu kn)
	{
		double f1, f2, fa, fb, tau = (Math.sqrt(5.0) - 1.0) / 2.0, x = 0.0, x1, x2;
		int count = 0;
					// �����ݒ�
		ind[0] = -1;
		x1     = b - tau * (b - a);
		x2     = a + tau * (b - a);
		f1     = kn.snx(x1, w, dw);
		f2     = kn.snx(x2, w, dw);
					// �v�Z
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
					// ���������ꍇ�̏���
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