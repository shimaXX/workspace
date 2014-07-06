package myUDF;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.apache.pig.EvalFunc;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.impl.logicalLayer.schema.Schema;

public class GetIntervalDateIndividuals extends EvalFunc<String> {

	private Date lastDate = null;
	private Date lastStampDate = null;
	private String output;

	@Override
	public String exec(Tuple input) throws IOException {
		// TODO Auto-generated method stub
		if (input == null || input.size() == 0) {
			return null;
		}

		try{
			//���t�̌^���Z�b�g
			SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
			
			//milli sec��day�ɒ������߂̏��Z�l��ݒ�
			long one_date_time = 1000*60*60*24;
			
			if(!input.get(0).toString().equals("NULL") && !input.get(1).toString().equals("NULL") ){
				//�ŏI�A�N�V��������terminal���擾
				String lastStamp = (String)input.get(0).toString();
				String str = (String)input.get(1).toString();
				
		    	this.lastDate = format.parse(str);
		    	this.lastStampDate = format.parse(lastStamp);
		
  	    		long lastStampDatetime = this.lastStampDate.getTime();
  	    		long terminalDatetime = this.lastDate.getTime();
  	    		Long tmp = (terminalDatetime - lastStampDatetime)/one_date_time;
  	    		this.output = Long.toString(tmp);
			}else{
				this.output = "NULL";
			}
  	    		
			return this.output;
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