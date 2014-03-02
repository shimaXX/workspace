package OnlineLearning;

public class Computer {
	private String lossType;
	private Model model;
	
	public Computer(String lossType, Model model){
		this.lossType = lossType;
		this.model = model;
	}
	
	public void ReadFile(){
		
	}
	
	public void Learning(){
		model.train(lossType);
	}

	public void Predict(){
		
	}
	
	public void SaveModel(){
		
	}
	
	public void ReadModel(){
		
	}	
}
