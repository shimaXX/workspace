package Aggregate;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.omg.CORBA.SystemException;

public class loadData {
	
	private final String CURRENT_PATH = new File("").getAbsolutePath();
	private final String PATH = CURRENT_PATH + "/works/";
	private String fname = null;
	
	public loadData(String fname){
		this.fname = fname;
	}
	
	public void getData() throws SystemException{		
		try(BufferedReader br = new BufferedReader(new FileReader(PATH+"input/"+this.fname)))
		{
			String line;
			Map<String, Integer> cntdomain = new HashMap<>();
			
			while ((line=br.readLine())!=null) {
				if(line!=null){
					String[] str = line.split("\t");
					
					String cookieid = str[0];
					String uid = str[1];
					String ip = str[2];
					String datetime = str[3];					
					String domain = getURLDomain.getDomainName(str[3]); // pre reffere
					String ref = str[4];					
					
					
					// count domain
					if(cntdomain.containsKey(domain)){
						cntdomain.put(domain, cntdomain.get(domain) + 1);
					}else{
						cntdomain.put(domain, 1);
					}
					System.out.println(domain);
					System.out.println(cntdomain.get(domain));					
				}
			}
			
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}	
}