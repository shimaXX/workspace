package BehaviorAnalysis;

/**********************************************/
/*     １行のデータから個々のデータを取り出す */
/*          coded by Y.Suganuma               */
/**********************************************/
public class Data {

	private int len, start, end;
	private String line;
	String data;
					// コンストラクタ
	Data (String l)
	{
		line  = l;
		len   = line.length();
		start = 0;
		end   = 0;
		data  = new String ();   // 次のデータ
	}
					// 次のデータの取り出し
					//   =0 : 成功，=-1 : 失敗
	int next()
	{
		int k = 0;
		if (start < len) {
			int sw = 0;
			while (sw == 0) {
				end = line.indexOf(" ", start); // 指定した文字を探索し先頭からの文字数を返す（該当の文字の手前まで）
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