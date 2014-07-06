package myUDF;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.pig.Accumulator;
import org.apache.pig.EvalFunc;
import org.apache.pig.data.BagFactory;
import org.apache.pig.data.DataBag;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.impl.logicalLayer.FrontendException;
import org.apache.pig.impl.logicalLayer.schema.Schema;


public class JuxtaposeNextVerb extends EvalFunc<DataBag> implements Accumulator<DataBag>
{
	  private DataBag outputBag;
	  private String last_verb;
	  private String last_sId;
	  private String postVerb;
	  private String sId;
	  private int size;
	  
	  public JuxtaposeNextVerb()
	  {
	    cleanup();
	  }

	  @Override
	  public DataBag exec(Tuple input) throws IOException
	  {
	    accumulate(input);
	    DataBag outputBag = getValue();
	    cleanup();

	    return outputBag;
	  }

	  @Override
	  public void accumulate(Tuple input) throws IOException
	  {
		size = input.size(); 
		String verb = null;
		String uid = null;
		
  	    for (Tuple t : (DataBag) input.get(0)) {
          verb = (String)t.get(1);
          uid = (String)t.get(0);
          this.sId = (String)t.get(3);
          List<String> list = new ArrayList<String>();
          
          if (this.last_sId == null){	//uidÇÃ1çsñ⁄ÇÃëÄçÏ
        	  this.last_verb = verb;
        	  this.last_sId = this.sId;
        	  continue;
          }else if (this.sId.equals(this.last_sId)){	  
        	  this.postVerb = verb;
          }else if (!this.sId.equals(this.last_sId)){
        	  this.last_verb = verb;
        	  this.last_sId = this.sId;
        	  continue;
          }
	      
          list.add(uid);
          list.add(this.last_verb);
          list.add(this.postVerb);
	      
          Tuple t_new = TupleFactory.getInstance().newTuple(list);
	      outputBag.add(t_new);
	      
	      this.last_verb = verb;
	      this.last_sId = this.sId;
	    }
  	    List<String> list = new ArrayList<String>();
        list.add(uid);
        list.add(verb);
        list.add("DEFECTION");
	      
        Tuple t_new = TupleFactory.getInstance().newTuple(list);
	    outputBag.add(t_new);
	  }

	  @Override
	  public DataBag getValue()
	  {
	    return outputBag;
	  }

	  @Override
	  public void cleanup()
	  {
	    this.last_verb = null;
	    this.outputBag = BagFactory.getInstance().newDefaultBag();
	    this.last_sId = null;
	    this.postVerb = null;
	    this.size = 0;
	  }

	  @Override
	  public Schema outputSchema(Schema input)
	  {
	    try {
	      Schema.FieldSchema inputFieldSchema = input.getField(0);

	      if (inputFieldSchema.type != DataType.BAG)
	      {
	        throw new RuntimeException("Expected a BAG as input");
	      }
	      
	      Schema inputBagSchema = inputFieldSchema.schema;
	      
	      if (inputBagSchema.getField(0).type != DataType.TUPLE)
	      {
	        throw new RuntimeException(String.format("Expected input bag to contain a TUPLE, but instead found %s",
	                                                 DataType.findTypeName(inputBagSchema.getField(0).type)));
	      }
	      
	      Schema inputTupleSchema = inputBagSchema.getField(0).schema;
	      
	      if (inputTupleSchema.getField(0).type != DataType.CHARARRAY)
	      {
	        throw new RuntimeException(String.format("Expected first element of tuple to be a CHARARRAY, but instead found %s",
	                                                 DataType.findTypeName(inputTupleSchema.getField(0).type)));
	      }
	      
	      Schema outputTupleSchema = new Schema();
	      
	      outputTupleSchema.add(new Schema.FieldSchema("uid", DataType.CHARARRAY));
	      outputTupleSchema.add(new Schema.FieldSchema("verb", DataType.CHARARRAY));
	      outputTupleSchema.add(new Schema.FieldSchema("postVerb", DataType.CHARARRAY));      
	      
	      return new Schema(new Schema.FieldSchema(getSchemaName(this.getClass()
	                                                             .getName()
	                                                             .toLowerCase(), input),
	                                           outputTupleSchema,
	                                           DataType.BAG));
	    }
	    catch (FrontendException e) {
	      throw new RuntimeException(e);
	    }
	  }
}
