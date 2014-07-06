package Adapter;

public class PrintBanner extends Banner implements Print {
	public PrintBanner(String string) {
		super(string); // 親のコンストラクタの呼び出し
	}
	public void printWeak() {
		showWithPaten();
	}
	public void printStrong() {
		showWithAster();
	}	
}
