package myUDF;

import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.apache.pig.AlgebraicEvalFunc;
import org.apache.pig.EvalFunc;
import org.apache.pig.backend.executionengine.ExecException;
import org.apache.pig.builtin.IsEmpty;
import org.apache.pig.data.BagFactory;
import org.apache.pig.data.DataBag;
import org.apache.pig.data.DataType;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.impl.logicalLayer.schema.Schema;

public class CountBadges extends AlgebraicEvalFunc<DataBag> {
	
	@Override
    public DataBag exec(Tuple input) throws IOException {
    	return null;
    }
    
    //init
    public String getInitial() {
    	return Initial.class.getName();
    }
    
    //med
    public String getIntermed() {
    	return Intermed.class.getName();
    }
    
    //final
    public String getFinal() {
    	return Final.class.getName();
    }
    
    static public class Initial extends EvalFunc<Tuple> {
    	
    	//inputの形は({(()),(()),(())・・・})となっている。普通は({(),(),()・・・})となっているはずなので、要注意。
        public Tuple exec(Tuple input) throws IOException {
        	DataBag b = (DataBag)input.get(0);
        	Iterator<Tuple> it = b.iterator();      	
        	if (!it.hasNext()) {
        		return null;
        	}
        	Tuple t = (Tuple)it.next().get(0);
        	if(t == null){
        		return null;
        	}
        	return TupleFactory.getInstance().newTuple(count(t));
        }
    }
    
    static public class Intermed extends EvalFunc<Tuple> {
        public Tuple exec(Tuple input) throws IOException {
        	return TupleFactory.getInstance().newTuple(sum(input));
        }
    }
    
    static public class Final extends EvalFunc<DataBag> {
        public DataBag exec(Tuple input) throws IOException {
        	Map<String, Long> map = sum(input);
        	DataBag bag = BagFactory.getInstance().newDefaultBag();
        	for(Map.Entry<String, Long> e : map.entrySet()) {
        		String key = e.getKey();
        	    Long value = e.getValue();
        	    
        	    Tuple t = TupleFactory.getInstance().newTuple(2);
        	    t.set(0, key);
        	    t.set(1, value);
        	    bag.add(t);
        	}
   
        	return bag;
        }
    }
    
    static protected Map<String, Long> count(Tuple input) throws ExecException {
        Map<String,Long> map = new HashMap<String,Long>();
        if(input.size() == 0){
        	return map;
        }
        for (int i=0; i < input.size(); i++){
        	String badge = (String)input.get(i);
			if(map.containsKey(badge)){
				map.put(badge,map.get(badge)+1);
			}else{
				map.put(badge,1L);
			}
        }
        return map;
    }
    
    static protected Map<String, Long> sum(Tuple input) throws ExecException, NumberFormatException {
        Map<String,Long> map = new HashMap<String,Long>();
        //TupleFactory t_new = TupleFactory.getInstance();
        
    	for (Tuple t : (DataBag) input.get(0)) {
    		map = merge(map, (Map<String, Long>)t.get(0));
    	} 	    	
        return map;
    }
    
    static protected Map<String, Long> merge(Map<String, Long> left,Map<String, Long> right) throws ExecException, NumberFormatException {
    	for(Map.Entry<String, Long> e : right.entrySet()) {
    		String key = e.getKey();
    	    if(left.containsKey(key)){
    	    	left.put(key, left.get(key) + e.getValue());
    	    }else{
    	    	left.put(key, e.getValue());
    	    }
    	}	
    	return left;
    }
}
