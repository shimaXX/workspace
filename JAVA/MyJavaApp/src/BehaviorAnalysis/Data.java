package BehaviorAnalysis;

/**********************************************/
/*     �P�s�̃f�[�^����X�̃f�[�^�����o�� */
/*          coded by Y.Suganuma               */
/**********************************************/
public class Data {

	private int len, start, end;
	private String line;
	String data;
					// �R���X�g���N�^
	Data (String l)
	{
		line  = l;
		len   = line.length();
		start = 0;
		end   = 0;
		data  = new String ();   // ���̃f�[�^
	}
					// ���̃f�[�^�̎��o��
					//   =0 : �����C=-1 : ���s
	int next()
	{
		int k = 0;
		if (start < len) {
			int sw = 0;
			while (sw == 0) {
				end = line.indexOf(" ", start); // �w�肵��������T�����擪����̕�������Ԃ��i�Y���̕����̎�O�܂Łj
				if (end >= 0) {
					if ((end - start) > 0) {
						data  = line.substring(start, end);
						sw    = 1;
					}
				}
				else {
					end = len;
					sw  = 1;
					if ((end - start) > 0)
						data  = line.substring(start, end);
					else
						k = -1;
				}
				start = end + 1;
			}
		}
		else
			k = -1;
		return k;
	}
}