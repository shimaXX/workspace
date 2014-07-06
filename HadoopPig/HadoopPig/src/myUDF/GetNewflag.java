package myUDF;

import java.io.IOException;
import java.util.Iterator;

import net.sf.json.JSONObject;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.BagFactory;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.impl.logicalLayer.schema.Schema;


public class GetNewflag extends EvalFunc<String> {
	BagFactory   bagFactory   = BagFactory.getInstance();
	TupleFactory tupleFactory = TupleFactory.getInstance();



	@Override
	public String exec(Tuple input) throws IOException {
		if (input == null || input.size() == 0) {
			return null;
		}
		
		try {  
			
			String str = (String) input.get(0).toString();
			
			JSONObject jo = JSONObject.fromObject(str); 
			Iterator<?> keys = jo.keys();
			String cmpNewStr = "new_flag";
			String sp_idKey = null;
			String output;
			
			for(int i=0; i<jo.size(); i++ ){
				String key = (String)keys.next();
				if(key.equals(cmpNewStr)){
					sp_idKey = (String)key;
					break;
				}else{
					sp_idKey = null;
				}
			}
						
			if(sp_idKey == null){
				output = null;	
			}else{
				String tmp = jo.getString(sp_idKey);
				output = cmpNewStr + "=" + tmp;
			}
			
			return output;
						
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
			thisSchema.add(new Schema.FieldSchema("newFlag", DataType.CHARARRAY));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.CHARARRAY));
		} catch (Exception e) {
			return null;
		}
	}

}