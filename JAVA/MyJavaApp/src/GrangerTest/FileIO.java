package GrangerTest;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.omg.CORBA.SystemException;

public class FileIO {
	private static final String CURRENT_PATH = new File("").getAbsolutePath();
	private static final String PATH = CURRENT_PATH+"/works/";
	
	//入力データの取得
	public static double[] GetData(String fname) throws SystemException{
		List<Double> list = new ArrayList<>();
		
		try(BufferedReader br = new BufferedReader(new FileReader(PATH+"input/"+fname)))
		{
			String line;
	
			while ((line = br.readLine()) != null) {
				if (line != null) {
					list.add(Double.parseDouble(line));
				}
			}
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		//System.out.println( (Double[])list.toArray(new Double[0]) );
		return LinearAlgebra.ConvertDoubleArray(list); //listからdouble型の配列に変換
	}

	//ファイル書き込み
	public static void WriteFile(double[][] x){
        try{
            FileWriter fw = new FileWriter(PATH+"output/result.txt");                
            for(int i=0;i<x[0].length;i++){
                fw.write(x[0][i]+","+x[1][i]+"\r\n");
            }
            fw.close();
       } catch(Exception e){
       }
	}	
}
