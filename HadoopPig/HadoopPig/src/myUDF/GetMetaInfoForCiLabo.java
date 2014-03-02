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


public class GetMetaInfoForCiLabo extends EvalFunc<String> {
	BagFactory   bagFactory   = BagFactory.getInstance();
	TupleFactory tupleFactory = TupleFactory.getInstance();



	@Override
	public String exec(Tuple input) throws IOException {
		if (input == null || input.size() == 0) {
			return null;
		}
		
		try {  
			String verb = (String) input.get(0).toString();			
			String str = (String) input.get(1).toString();
			
			JSONObject jo = JSONObject.fromObject(str); 
			Iterator<?> keys = jo.keys();
			String cmpCartStr = "cart_category";		//cart
			String cmpViewStr = "view_category";		//view, pmp_view
			String cmpCommuStr = "commu_category";		//pmp_commu 
			String cmpMailStr = "mail_category";		//mail
			String sp_idKey = null;
			String output;
			
			for(int i=0; i<jo.size(); i++ ){
				String key = (String)keys.next();
				if(key.equals(cmpCartStr) || key.equals(cmpViewStr) ||
						key.equals(cmpCommuStr) || key.equals(cmpMailStr)){
					sp_idKey = (String)key;
					break;
				}else{
					sp_idKey = null;
				}
			}
						
			if(sp_idKey == null){
				output = verb;	
			}else{
				String tmp = verb + ":" + jo.getString(sp_idKey);
				output = tmp;
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
			thisSchema.add(new Schema.FieldSchema("metaInfo", DataType.CHARARRAY));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.CHARARRAY));
		} catch (Exception e) {
			return null;
		}
	}

}