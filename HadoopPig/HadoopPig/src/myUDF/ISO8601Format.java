package myUDF;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.*;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.Tuple;

public class ISO8601Format extends EvalFunc<String> {

	Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
	private SimpleDateFormat dateFormatInput = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss" , Locale.JAPAN);
	private SimpleDateFormat sdfIso8601BasicFormatUtc = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.JAPAN);
	//sdfIso8601BasicFormatUtc.setTimeZone(cal.getTimeZone());
	
	@Override
	public String exec(Tuple input) throws IOException {
		if (input == null || input.size() == 0) {
			return null;
		}
				
		try {  
			
			//受け取ったタプルの0盤目の項目を文字列として取得
			String str = (String) input.get(0);
			
			//文字列をDateに変換
			Date dateInput = dateFormatInput.parse(str) ;
			
			//Dateから文字列に再変換し、値を返す
			return sdfIso8601BasicFormatUtc.format(dateInput);
		} catch (Exception e) {  
			throw new IOException("Caught exception processing input row  " + input.get(0), e);  
		} 		
	}	
}
