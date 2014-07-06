package myUDF;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;
import java.util.Locale;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.DataBag;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.logicalLayer.schema.Schema;

public class GetSessionTime extends EvalFunc<Double> {
	  private double output;
	  private Date firstTime;
	  private Date lastTime;

	  @Override
	  public Double exec(Tuple input) throws IOException
	  {
		  SimpleDateFormat dateFormatInput = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.JAPAN);
		  //SimpleDateFormat dateFormatInput = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		  this.firstTime = null;
		  this.lastTime = null;
		  
		  long datetime1;
		  long datetime2;
		  long one_minites_time = 1000;
	  
		  if (input == null || input.size() == 0) {
			return null;
		  }
					
		  try {  
			  	//受け取ったタプルの0盤目の項目を文字列として取得
			  	DataBag values = (DataBag)input.get(0);
			  	Iterator<Tuple> it = values.iterator();
			  	
			  	//要素がゼロ個だったらnullを返す
			  	if(!it.hasNext()){
			  		return null;
			  	}
			  	
			  	//1つ目の要素を取得
			  	String firstDate = it.next().get(0).toString();
			  	
			  	//要素が1個だったらnullを返す
			  	if(!it.hasNext()){
			  		return null;
			  	}
			  	
		  		//文字列をDateに変換
			  	try {
			  		this.firstTime = dateFormatInput.parse(firstDate);
			  	}catch (ParseException e){
			  		e.printStackTrace();
			  	}
			  	
			  	for(Tuple t: (DataBag)input.get(0)){
			  		if(it.hasNext()){
			  			try{
			  				this.lastTime = dateFormatInput.parse(it.next().get(0).toString());
			  			}catch (ParseException e){
			  				e.printStackTrace();
			  			}
				  	}
			  	}
			  	
			  	datetime1 = this.lastTime.getTime();
			  	datetime2 = this.firstTime.getTime();
			  	
			  	output = (datetime1 - datetime2)/one_minites_time;
			  	
			  	//差を秒で返す
			  	return output;
		  } catch (Exception e) {  
			  	throw new IOException("Caught exception processing input row  " + input.get(0), e);  
		  } 		  
	  }
		  
	//データ型の指定
	@Override
	public Schema outputSchema(Schema input) {
		try {
			Schema thisSchema = new Schema();

			// バッグ内の項目の定義（項目名とデータ型）
			thisSchema.add(new Schema.FieldSchema("interval", DataType.DOUBLE));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.DOUBLE));
		} catch (Exception e) {
			return null;
		}
	}	
}
