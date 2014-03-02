package myUDF;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
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

public class MergeVerb extends EvalFunc<DataBag> implements Accumulator<DataBag>
{
	  private DataBag outputBag;
	  private String last_verb;
	  private String exExVerb;
	  private int Id;
	  
	  public MergeVerb()
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
		List<String> list = new ArrayList<String>();
		
	    for (Tuple t : (DataBag) input.get(0)) {
	        String verb = (String)t.get(2);
	            
	    	if (this.Id == 0){	//uidÇÃ1çsñ⁄ÇÃëÄçÏ
	    			
	    		this.exExVerb = verb;
	    		list.add(verb);
	    	
	    		this.Id += 1;
	    	}else if(this.Id == 1) {
	    		if(this.exExVerb.equals(verb)){
	    			continue;
	    		}else{
	    			this.last_verb = verb;
	    				
		    		list.add(verb);
		    
		    		this.Id += 1;
	    		}
	    	}else{
	    		if(this.exExVerb.equals(verb) || this.last_verb.equals(verb)) {
	    			continue;
	    		}else {
	    			this.exExVerb = this.last_verb;
	    			this.last_verb = verb;
	    				
		    		list.add(verb);
		   			this.Id += 1;
	    		}
	    	}
	    }
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
		this.exExVerb = null;
	    this.last_verb = null;
	    this.outputBag = BagFactory.getInstance().newDefaultBag();
	    this.Id = 0;
	  }

	  public Integer count(Iterator<Tuple> it)
	  {
		  int cnt = 0;
		  while (it.hasNext()) {
			  it.next();
			  cnt +=1;
			} 
		  return cnt;
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
	      
	      outputTupleSchema.add(new Schema.FieldSchema("verb", DataType.CHARARRAY));    
	      
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