package myUDF;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.logicalLayer.schema.Schema;

public class GetNextDate extends EvalFunc<String> {
	
	private String output;
	
	@Override
	public String exec(Tuple input) throws IOException
	{	
		if (input == null || input.size() == 0) {
			return null;
		}
	
		try {
			String str = (String)input.get(0).toString();
			int year = Integer.parseInt(str.substring(0, 4));
		    int month = Integer.parseInt(str.substring(5, 7));
		    int day = Integer.parseInt(str.substring(8, 10));
		    //Calendarクラスのオブジェクトを生成
		    Calendar cal = Calendar.getInstance();
			
		    // strDateをセット
		    cal.set(year, month, day);

		    // 1日加算
		    cal.add(Calendar.DATE, 1);

		    String yearStr = String.valueOf(cal.get(Calendar.YEAR));
		    String monthStr = String.format("%02d" ,cal.get(Calendar.MONTH));
		    String dayStr = String.format("%02d" ,cal.get(Calendar.DATE));
		    this.output = yearStr + "-" + monthStr + "-" + dayStr; 
		    return this.output;
	    
		
		} catch (Exception e) {  
			throw new IOException("Caught exception processing input row  ", e);  
		} 		
	}
	
	//データ型の指定
	@Override
	public Schema outputSchema(Schema input) {
		try {
			Schema thisSchema = new Schema();

			// バッグ内の項目の定義（項目名とデータ型）
			thisSchema.add(new Schema.FieldSchema("nextDate", DataType.CHARARRAY));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.CHARARRAY));
		} catch (Exception e) {
			return null;
		}
	}
}
