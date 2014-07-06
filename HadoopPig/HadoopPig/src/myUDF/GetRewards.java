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
				//rewars�͕K��key�Ƃ��đ��݂��Ă���B���̂��ߏ����͍s��Ȃ��B
				//rewards = null;	
			//�L�[�����݂���ꍇ
			}else{
				String s = jo.getString(sp_idKey);
				JSONArray jsonArray = JSONArray.fromObject(s);
				//1�A�N�e�B�r�e�B��1�ȏ��rewards���擾�����ꍇ
				if(jsonArray.size() > 0){
					 for(int i=0; i<jsonArray.size(); i++ ){
						 JSONObject tmp  = jsonArray.getJSONObject(i);
						 //�Ƃ肠�������O�����擾�B����type����邩�����B
						 String name = tmp.getString("name");
						 list.add(name);
					 }
				//reward��S���l�����Ă��Ȃ��ꍇ
				}else{
					list.add(null);
				}
			}
			//tuple�ɓ����
			Tuple t_new = TupleFactory.getInstance().newTuple(list);
			
			
			return t_new;
						
		} catch (Exception e) {  
			throw new IOException("Caught exception processing input row  ", e);  
		} 		
	}
	
	//�f�[�^�^�̎w��
	@Override
	public Schema outputSchema(Schema input) {
		try {
			Schema thisSchema = new Schema();

			// �o�b�O���̍��ڂ̒�`�i���ږ��ƃf�[�^�^�j
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