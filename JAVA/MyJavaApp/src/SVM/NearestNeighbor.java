package SVM;

//NearestNeighbor.java
import java.util.*;

class NearestNeighbor implements LearningMachine {
  List<Map.Entry<Integer, double[]>> patterns = 
          new ArrayList<Map.Entry<Integer, double[]>>();

  public static void main(String[] args) {
      new MachineLearning("NN�@", new NearestNeighbor());
  }

  public void learn(int cls, double[] data) {
      patterns.add(new AbstractMap.SimpleEntry(cls, data));
  }

  public int trial(double[] data) {
      int cls = 0;
      //��ԋ߂��p�^�[�������߂�
      double mindist = Double.POSITIVE_INFINITY;
      for (Map.Entry<Integer, double[]> entry : patterns) {
          double[] ss = entry.getValue();
          if (ss.length != data.length) {
              System.out.println("�ւ�ȃf�[�^");
              continue;
          }
          //�f�[�^�Ԃ̋��������߂�
          double dist = 0;
          for (int i = 0; i < ss.length; ++i) {
              dist += (ss[i] - data[i]) * (ss[i] - data[i]);
          }
          if (mindist > dist) {
              mindist = dist;
              cls = entry.getKey();
          }
      }
      return cls;
  }
}