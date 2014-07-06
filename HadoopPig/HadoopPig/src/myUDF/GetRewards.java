package myUDF;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.BagFactory;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.impl.logicalLayer.schema.Schema;


public class GetRewards extends EvalFunc<Tuple> {
	BagFactory   bagFactory   = BagFactory.getInstance();
	TupleFactory tupleFactory = TupleFactory.getInstance();



	@Override
	public Tuple exec(Tuple input) throws IOException {
		if (input == null || input.size() == 0) {
			return null;
		}
		
		try {
			String str = (String) input.get(0).toString();
						
			JSONObject jo = JSONObject.fromObject(str);

			if(jo == null || jo.isEmpty()){
				return null;
			}

			
			Iterator<?> keys = jo.keys();
			String cmpRewardsStr = "rewards";
			String sp_idKey = null;
			List<String> list = new ArrayList<String>();
			
			for(int i=0; i<jo.size(); i++ ){
				String key = (String)keys.next();
				if(key.equals(cmpRewardsStr)){
					sp_idKey = (String)key;
					break;
				}else{
					sp_idKey = null;
				}
			}
						
			if(sp_idKey == null){
				//rewarsは必ずkeyとして存在している。そのため処理は行わない。
				//rewards = null;	
			//キーが存在する場合
			}else{
				String s = jo.getString(sp_idKey);
				JSONArray jsonArray = JSONArray.fromObject(s);
				//1アクティビティで1以上のrewardsを取得した場合
				if(jsonArray.size() > 0){
					 for(int i=0; i<jsonArray.size(); i++ ){
						 JSONObject tmp  = jsonArray.getJSONObject(i);
						 //とりあえず名前だけ取得。今後typeも取るか検討。
						 String name = tmp.getString("name");
						 list.add(name);
					 }
				//rewardを全く獲得していない場合
				}else{
					list.add(null);
				}
			}
			//tupleに入れる
			Tuple t_new = TupleFactory.getInstance().newTuple(list);
			
			
			return t_new;
						
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
			thisSchema.add(new Schema.FieldSchema("rewards", DataType.TUPLE));

			return new Schema(new Schema.FieldSchema(
				getSchemaName(getClass().getName().toLowerCase(), input),
				thisSchema,
				DataType.TUPLE));
		} catch (Exception e) {
			return null;
		}
	}

}