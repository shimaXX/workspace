# coding: utf-8

import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import os
from zipfile import ZipFile
from StringIO import StringIO

def get_link_info_str(ticker_symbol, base_url):
    url = base_url+ticker_symbol
    response = requests.get(url)
    return response.text
    
def get_link(tree, namespace):
    #print ET.tostring(tree)
    yuho_dict = defaultdict(dict)
    for el in tree.findall('.//'+namespace+'entry'):
        title = el.find(namespace+'title').text
        if not is_yuho(title): continue
        print 'writing:',title[:30],'...'
        _id = el.find(namespace+'id').text
        link = el.find('./'+namespace+'link[@type="application/zip"]')
        url = link.attrib['href']
        yuho_dict[_id] = {'id':_id,'title':title,'url':url}
    return yuho_dict
    
def is_yuho(title):
    if u'有価証券報告書' in unicode(title):
        return True
    else:
        return False
    
def write_download_info(ofname):
    with open(ofname,'w') as of:
        json.dump(dat_download, of, indent=4)
    
def download_all_xbrl_files(download_info_dict,directory_path):    
    for ticker_symbol, info_dicts in download_info_dict.items():
        save_path = directory_path+ticker_symbol
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        for _id, info_dict in info_dicts.items():
            _download_xbrl_file(info_dict['url'],_id,save_path)
    
def _download_xbrl_file(url,_id,save_path):
    r = requests.get(url)
    if r.ok:
        #print url
        path = save_path+'/'+_id
        if not os.path.exists(path):
            os.mkdir(path)
        r = requests.get(url)
        z = ZipFile(StringIO(r.content))
        z.extractall(path) # unzip the file and save files to path.
    
if __name__=='__main__':
    base_url = 'http://resource.ufocatch.com/atom/edinetx/query/'
    namespace = '{http://www.w3.org/2005/Atom}'
    t_symbols = ('1301','2432',)
    
    for t_symbol in t_symbols:
        response_string = get_link_info_str(t_symbol, base_url)
        ET_tree = ET.fromstring( response_string )
        ET.register_namespace('',namespace[1:-1])
        
        dat_download = defaultdict(dict)
        # get download file info
        info_dict = get_link(ET_tree,namespace)
        dat_download[t_symbol] = info_dict
        
        ofname = os.getcwd()+'/downloaded_info/dat_download_'+t_symbol+'.json'
        write_download_info(ofname)
        
        directory_path = os.getcwd()+'/xbrl_files/'
        download_all_xbrl_files(dat_download,directory_path)