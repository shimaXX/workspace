package Aggregate;

//http://www.ne.jp/asahi/hishidama/home/tech/java/regexp.html
//http://syunpon.com/programing/java/sample/substring.shtml#sample4

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.net.URLEncoder;

public class ApacheLogAnalyzer {
    public static String[] getKeywords(String url) throws UnsupportedEncodingException
    {
        String path_input  = "C:Program Fileshogeaccess_bak_for_anylyze.log";//Apache�̃��O
        String path_output = "C:Program FileshogeApacheLogAnalyzer.csv";//�o��CSV
        String url_google ="http://www.google.co.jp/search";
        String url_yahoo ="http://search.yahoo.co.jp/search";
 
 
            Map<String,Integer> dic =new HashMap<String,Integer>();
            String line ="";
        //���O���
        String query ="";
        String[] words = null;
        //�����G���W����URL���܂܂�Ă��邩
        if(line.indexOf(url_google)>=0)//google
        {
        	Matcher m = Pattern.compile(url_google +".*?q=(.*?)[&$]").matcher(line); //&��$�Ƀ}�b�`
            if(m.find())
            {
                query = line.substring(m.end()+1);
            }
        }
        else if(line.indexOf(url_yahoo)>=0)//yahoo
        {
            Matcher m = Pattern.compile(url_yahoo +".*?p=(.*?)[&$]").matcher(line); //&��$�Ƀ}�b�`
            if(m.find())
            {
                query = line.substring(m.end()+1);
            }
        }
        if(query !="")
        {
            //URL�f�R�[�h
            query = URLDecoder.decode(query,"utf-8");//GetEncoding("SJIS"));
 
                //�󔒕����ŋ�؂�A�z��Ƃ���
            query = query.replaceAll("�@"," ");//�S�p�X�y�[�X�𔼊p�X�y�[�X�ɒu��
            words = query.split(" ");//�󔒂ŕ���
        }
        
		return words;            
    }
    
    public static void cntWord(Map<String, Integer> wordmap, String[] words){
        //���[�h���Ƃ̌������𐔂���
    	for(String word : words){
	        if(word !="")
	        {
	            if(!wordmap.containsKey(word))
	            {
	            	wordmap.put(word, 1);//�ǉ�
	            }
	            else
	            {
	                wordmap.put(word, wordmap.get(word)+1);//�J�E���g�A�b�v
	            }
	        } 
    	}
    }
    
    public static void valueSort(Map<String, Integer> tmap){
        // List ���� (�\�[�g�p)
        List<Map.Entry<String,Integer>> entries = 
              new ArrayList<Map.Entry<String,Integer>>(tmap.entrySet());
        Collections.sort(entries, new Comparator<Map.Entry<String,Integer>>() {
 
            @Override
            public int compare(
                  Entry<String,Integer> entry1, Entry<String,Integer> entry2) {
                return ((Integer)entry2.getValue()).compareTo((Integer)entry1.getValue());
            }
        });
    }
}