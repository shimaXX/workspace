package SVM;

//LearningMachine.java
public interface LearningMachine {
  //�w�K
  void learn(int cls, double[] data);
  //�]��
  int trial(double[] data);
}