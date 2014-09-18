# coding: utf-8

from xbrl import XBRLParser
import os, re
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup as soup


base_path = os.getcwd()+'/xbrl_files/1301/'
dir = 'ED2014062400389/S10025H8/XBRL/PublicDoc/'
base_filename = base_path+dir+'jpcrp030000-asr-001_E00012-000_2014-03-31_01_2014-06-24'

def get_facts_info():
    xbrl_file_name = base_filename+'.xbrl'

    # parse xbrl file
    xbrl = XBRLParser.parse(file(xbrl_file_name)) # beautiful soup type object
    facts_dict = defaultdict(list)
    
    #print xbrl
    name_space = 'j*cor'
    for node in xbrl.find_all(name=re.compile(name_space+':*')):
        if 'xsi:nil' in node.attrs:
            if node.attrs['xsi:nil']=='true':
                continue
        
        facts_dict['element_id'].append( node.name.split(':')[1] )
        facts_dict['amount'].append( node.string )
        
        facts_dict['context_ref'].append(
                    get_attrib_value(node, 'contextref') )
        facts_dict['unit_ref'].append( 
                    get_attrib_value(node, 'unitref') )
        facts_dict['decimals'].append(
                    get_attrib_value(node, 'decimals') )
    #doc_info_dict = get_document_info(xbrl)
    return facts_dict
    #return amount_info_dict

def get_attrib_value(node, attrib):
    if attrib in node.attrs.keys():
        return node.attrs[attrib]
    else:
        return None

def get_document_info(xbrl):
    doc_info_dict = defaultdict(list)
    documentinfo_name_space = 'jpfr-di'
    for node in xbrl.find_all(name=re.compile(documentinfo_name_space+':*')):
        if 'xsi:nil' in node.attrs:
            if node.attrs['xsi:nil']=='true':
                continue
    
        doc_info_dict['element_id'].append( node.name.replace(documentinfo_name_space+':', '') )
        doc_info_dict['document'].append( node.string )
    return doc_info_dict
    
def get_label_info(namespaces):
    label_dict = defaultdict(list)
    
    label_file_name = base_filename+'_lab.xml'
    ET.register_namespace('','http://www.w3.org/2005/Atom')
    labels = ET.parse(label_file_name)
    
    for label_node in labels.findall('.//link:label',namespaces=namespaces):
        if is_target_node(label_node, namespaces):
            label = label_node.attrib['{'+namespaces['xlink']+'}label']
            element_id = label.split('_')[2]
            label_dict['ement_id'].append( element_id )
            label_dict['label_string'].append( label_node.text)
    return label_dict

def _get_label_info(namespaces):
    label_dict = defaultdict(list)
    
    label_file_name = base_filename+'_lab.xml'
    #ET.register_namespace('','http://www.w3.org/2005/Atom')
    labels = soup(open(label_file_name).read(),'xml')
    
    for label_node in labels.find_all('link:label'):
        if is_target_node(label_node, namespaces):
            label = label_node.attrib['xlink;label']
            element_id = label.split('_')[2]
            label_dict['ement_id'].append( element_id )
            label_dict['label_string'].append( label_node.text)
    return label_dict
        
def is_target_node(node, namespaces):
    if node.attr['xml:lang']=='ja' and \
        node.attr['xlink:role']=='http://www.xbrl.org/2003/role/documentation':
        return True
    else:
        return False
 
def main(namespaces):
    df_xbrl_labels = pd.DataFrame( _get_label_info(namespaces) )
    df_xbrl_facts = pd.DataFrame( get_facts_info() )
    print df_xbrl_labels
    print df_xbrl_facts
    
    dat_fi = pd.merge(df_xbrl_labels, df_xbrl_facts,how='inner')
    print dat_fi
    
if __name__=='__main__':
    namespaces = {'link': 'http://www.xbrl.org/2003/linkbase',
              'xml':'http://www.w3.org/XML/1998/namespace',
              'xlink':'http://www.w3.org/1999/xlink',
              'xsi':'http://www.w3.org/2001/XMLSchema-instance'
              }
    main(namespaces)