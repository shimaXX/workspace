package Aggregate;
//http://www.java2s.com/Code/Jar/c/Downloadcomgoogleguava160jar.htm

import java.net.*;

import com.google.common.net.*;


public class getURLDomain {

	public static String getDomainName(String str) throws MalformedURLException{
		URL url = new URL(str);
		return InternetDomainName.from(url.getHost()).topPrivateDomain().name().toString();
	}
}
