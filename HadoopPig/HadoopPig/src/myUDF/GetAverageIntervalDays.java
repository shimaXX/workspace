package myUDF;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import org.apache.pig.EvalFunc;
import org.apache.pig.data.DataBag;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.logicalLayer.schema.Schema;

public class GetAverageIntervalDays extends EvalFunc<String> {
	  private String output;
	  private Date last_day;
	  private Date postDay;
	  private int Id;
	  private double interval;
	  private double intervalSum;
	  private double vcnt;

	  @Override
	  public String exec(Tuple input) throws IOException
	  {
//		SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");

	    this.last_day = null;
	    this.Id = 0;
	    this.postDay = null;
	    this.vcnt = 0;
		this.interval=0;
		this.intervalSum=0;
		
		long datetime1;
		long datetime2;
		long one_date_time = 1000*60*60*24;
		
		
	    for (Tuple t : (DataBag) input.get(0)) {
	    	String day = (String)t.get(0);
        
        	if (this.Id == 0){	//uidの1行目の操作
      	    	try {
      	    		this.last_day = format.parse(day);
      	    	} catch (ParseException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
      	    	this.Id = 1;
      	    	this.vcnt = 0.00000001;
      	    	continue;
        	}else{	  
      	    	try {
      	    		this.postDay = format.parse(day);
      	    	} catch (ParseException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
      	    	datetime1 = last_day.getTime();
      	    	datetime2 = postDay.getTime();
      	    
      	    	this.interval = (datetime2 - datetime1)/one_date_time;
      	    	this.intervalSum += this.interval;
      	    	this.vcnt +=1;
      	    	     	    	
      	    	this.last_day = postDay;
        	}  	      
	    }
	    
	    if (this.intervalSum > 0) this.output = Double.toString( (double)((int)((this.intervalSum/(int)this.vcnt)*100d))/100d );
	    else this.output = null;
	    return this.output;
	  }

	
	//データ型の指定
	@Override
	public Schema outputSchema(Schema input) {
		try {
			Schema thisSchema = new Schema();

			// バッグ内の項目の定義（項目名とデータ型）
			thisSchema.add(new Schema.FieldSchema("interval", DataType.CHARARRAY));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.CHARARRAY));
		} catch (Exception e) {
			return null;
		}
	}
}
