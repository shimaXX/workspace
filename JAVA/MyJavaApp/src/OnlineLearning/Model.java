package OnlineLearning;

public interface Model {
	public abstract void train(String lossType);
	public abstract void predict();
	public abstract void saveModel();
	public abstract void readModel();
}
