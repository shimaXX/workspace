package Adapter;

public class PrintBanner extends Banner implements Print {
	public PrintBanner(String string) {
		super(string); // �e�̃R���X�g���N�^�̌Ăяo��
	}
	public void printWeak() {
		showWithPaten();
	}
	public void printStrong() {
		showWithAster();
	}	
}
