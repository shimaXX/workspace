# coding: utf-8

from xbrl import XBRLParser
import os, re
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
import urllib2


class XbrlParser(XBRLParser):
    def __init__(self, xbrl_filename):
        self.xbrl_filename = xbrl_filename
        self.base_filename = xbrl_filename.replace('.xbrl','')
    
    def parse_xbrl(self,namespaces):
        result = defaultdict(dict)
        result['facts']=self.get_facts_info()
        
        label_file_name = self.base_filename+'_lab.xml'
        ET.register_namespace('','http://www.w3.org/2005/Atom')
        labels = ET.parse(label_file_name)
        
        # get enterprise taxonomy
        extended_labels = self.get_label_info(namespaces,labels)
        
        # get base link
        base_labels = self.get_base_label_info(namespaces)
        
        extended_labels = extended_labels.append(base_labels,ignore_index=True)
        result['labels'] = extended_labels
        result['presentation']=self.get_presentation_info(namespaces)
        return result

    def get_base_label_info(self,namespaces):
        base_file_path = os.getcwd()+'/base_labels/'
        if not os.path.exists(base_file_path):
            os.mkdir(base_file_path)
        base_labels = None
        
        # get common taxonomy
        for link_base in self.get_link_base(namespaces):
            file_path = base_file_path + link_base.strip().split('/')[-1]
            
            if os.path.exists(file_path):
                tmp_base_labels = pd.read_csv(file_path)
            else:
                print 'creating ', link_base, 'base label data...'
                response = urllib2.urlopen(link_base)
                html = response.read()
                ET.register_namespace('','http://www.xbrl.org/2003/linkbase')
                labels = ET.fromstring(html)
                labels = labels.findall('.//link:labelLink',namespaces=namespaces)[0]
                
                tmp_base_labels = self.get_label_info(namespaces,labels)
                tmp_base_labels.to_csv(file_path,index=False)                
            if base_labels is not None:
                base_labels = base_labels.append(tmp_base_labels,ignore_index=True)
            else:
                base_labels = tmp_base_labels
        return base_labels

    def concat_dictionary(self,dict1,dict2):
        for key in dict1.keys():
            dict1[key] = dict1[key]+dict2[key]
        return dict1
        
    def get_facts_info(self):
        """
        return(element_id, amount, context_ref, unit_ref, decimals)
        """
        # parse xbrl file
        xbrl = XBRLParser.parse(file(self.xbrl_filename)) # beautiful soup type object
        facts_dict = defaultdict(list)
        
        #print xbrl
        name_space = 'jp*'
        for node in xbrl.find_all(name=re.compile(name_space+':*')):
            if 'xsi:nil' in node.attrs:
                if node.attrs['xsi:nil']=='true':
                    continue
            
            facts_dict['element_id'].append( node.name.replace(':','_') )
            facts_dict['amount'].append( node.string )
            
            facts_dict['context_ref'].append(
                        self.get_attrib_value(node, 'contextref') )
            facts_dict['unit_ref'].append( 
                        self.get_attrib_value(node, 'unitref') )
            facts_dict['decimals'].append(
                        self.get_attrib_value(node, 'decimals') )
        return pd.DataFrame( facts_dict )
    
    def get_attrib_value(self, node, attrib):
        if attrib in node.attrs.keys():
            return node.attrs[attrib]
        else:
            return None
    
    def get_link_base(self,namespaces):
        label_file_name = self.base_filename+'.xsd'
        ET.register_namespace('','http://www.w3.org/2001/XMLSchema')
        labels = ET.parse(label_file_name)        
        linkbases = labels.findall('.//link:linkbaseRef',namespaces=namespaces)

        link_base = []
        for link_node in linkbases:
            link_href = link_node.attrib['{'+namespaces['xlink']+'}href']
            if '_lab.xml' in link_href and 'http://' in link_href:
                link_base.append(link_href) 
        return link_base
    
    def get_label_info(self, namespaces,labels):
        """
        return(element_id, label_string, lang, label_role, href)
        """
        label_dict = defaultdict(list)
        
        #label_file_name = self.base_filename+'_lab.xml'
        #ET.register_namespace('','http://www.w3.org/2005/Atom')
        #labels = ET.parse(label_file_name)
        
        for label_node in labels.findall('.//link:label',namespaces=namespaces):
            label_label = label_node.attrib['{'+namespaces['xlink']+'}label']
            
            for labelArc_node in labels.findall('.//link:labelArc',namespaces=namespaces):
                if label_label != labelArc_node.attrib['{'+namespaces['xlink']+'}to']:
                    continue
                
                for loc_node in labels.findall('.//link:loc',namespaces=namespaces):
                    loc_label = loc_node.attrib['{'+namespaces['xlink']+'}label']
                    if loc_label != labelArc_node.attrib['{'+namespaces['xlink']+'}from']:
                        continue
    
                    lang = label_node.attrib['{'+namespaces['xml']+'}lang']
                    label_role = label_node.attrib['{'+namespaces['xlink']+'}role']
                    href = loc_node.attrib['{'+namespaces['xlink']+'}href']
                    
                    label_dict['element_id'].append( href.split('#')[1].lower() )
                    label_dict['label_string'].append( label_node.text)
                    label_dict['lang'].append( lang )
                    label_dict['label_role'].append( label_role )
                    label_dict['href'].append( href )
        return pd.DataFrame( label_dict )

    def get_presentation_info(self, namespaces):
        """
        return(element_id, label_string, lang, label_role, href)
        """
        type_dict = defaultdict(list)
        
        label_file_name = self.base_filename+'_pre.xml'
        ET.register_namespace('','http://www.w3.org/2005/Atom')
        types = ET.parse(label_file_name)
        
        for type_link_node in types.findall('.//link:presentationLink',namespaces=namespaces):
            for type_arc_node in type_link_node.findall('.//link:presentationArc',namespaces=namespaces):
                type_arc_from = type_arc_node.attrib['{'+namespaces['xlink']+'}from']
                type_arc_to = type_arc_node.attrib['{'+namespaces['xlink']+'}to']
                
                matches = 0
                for loc_node in type_link_node.findall('.//link:loc',namespaces=namespaces):
                    loc_label = loc_node.attrib['{'+namespaces['xlink']+'}label']
                    
                    if loc_label == type_arc_from:
                        if '{'+namespaces['xlink']+'}href' in loc_node.attrib.keys():
                            href_str = loc_node.attrib['{'+namespaces['xlink']+'}href']
                            type_dict['from_href'].append( href_str )
                            type_dict['from_element_id'].append( href_str.split('#')[1].lower() )
                            matches += 1
                    elif loc_label == type_arc_to:
                        if '{'+namespaces['xlink']+'}href' in loc_node.attrib.keys():
                            href_str = loc_node.attrib['{'+namespaces['xlink']+'}href']
                            type_dict['to_href'].append( href_str )
                            type_dict['to_element_id'].append( href_str.split('#')[1].lower() )
                            matches += 1                    
                    if matches==2: break
                    
                role_id = type_link_node.attrib['{'+namespaces['xlink']+'}role']
                arcrole = type_arc_node.attrib['{'+namespaces['xlink']+'}arcrole']
                order = self.get_xml_attrib_value(type_arc_node, 'order')
                closed = self.get_xml_attrib_value(type_arc_node, 'closed')
                usable = self.get_xml_attrib_value(type_arc_node, 'usable')
                context_element = self.get_xml_attrib_value(type_arc_node, 'contextElement')
                preferred_label = self.get_xml_attrib_value(type_arc_node, 'preferredLabel')
                
                type_dict['role_id'].append( role_id )
                type_dict['arcrole'].append( arcrole )
                type_dict['order'].append( order )
                type_dict['closed'].append( closed )
                type_dict['usable'].append( usable )                
                type_dict['context_element'].append( context_element )
                type_dict['preferred_label'].append( preferred_label )
        return pd.DataFrame( type_dict )

    def get_xml_attrib_value(self, node, attrib):
        if attrib in node.attrib.keys():
            return node.attrib[attrib]
        else:
            return None
            
    def extract_target_data(self, df, element_id=None, label_string=None, \
                                lang=None, label_role=None, href=None):
        if element_id is not None:
            df = df.ix[df['element_id']==element_id,:]
        if label_string is not None:
            df = df.ix[df.label_string.str.contains(label_string),:]
        if lang is not None:
            df = df.ix[df['lang']==lang,:]
        if label_role is not None:
            df = df.ix[df.label_role.str.contains(label_role),:]
        if href is not None:
            df = df.ix[df['href']==href,:]
        return df
     
    def gather_descendant(self,df,parent):
        children = df.to_element_id.ix[df.from_element_id==parent]
        return children.append( children.apply(lambda x: self.gather_descendant(df, x)) )
    
    def get_specific_account_name_info(self,dat_fi,df_descendant):
        result = None
        for label_id in df_descendant.ix[:,0].values:
            if result is None:
                result = dat_fi.ix[dat_fi.element_id==label_id,:]
            else:
                result = result.append(dat_fi.ix[dat_fi.element_id==label_id,:], ignore_index=True)
        return result
        
def main(namespaces):
    base_path = os.getcwd()+'/xbrl_files/1301/'
    _dir = 'ED2014062400389/S10025H8/XBRL/PublicDoc/'
    xbrl_filename = base_path+_dir+'jpcrp030000-asr-001_E00012-000_2014-03-31_01_2014-06-24.xbrl'

    # get data
    xp = XbrlParser(xbrl_filename)
    
    print 'getting data...'
    xbrl_persed = xp.parse_xbrl(namespaces)
    print 'done'
    
    df_xbrl_facts = xbrl_persed['facts'] # 金額の定義及び文書情報の定義情報
    df_xbrl_labels = xbrl_persed['labels'] # 名称リンク情報
    df_xbrl_presentation = xbrl_persed['presentation'] # 表示リンク情報

    # extract labels data
    df_xbrl_labels = xp.extract_target_data(df_xbrl_labels, lang='ja') 
                            #label_role='http://www.xbrl.org/2003/role/documentation')
                            #label_role='documentation')
    
    # De-duplication of labels data
    df_xbrl_labels = df_xbrl_labels.drop_duplicates()
    
    dat_fi = pd.merge(df_xbrl_labels, df_xbrl_facts, on='element_id',how='inner')
    
    # specify duration
    dat_fi_cyi = dat_fi.ix[dat_fi.context_ref=='CurrentYearInstant'] # 当期 時点
    # 流動資産のelement_idのみ取得
    parent = df_xbrl_labels.element_id.ix[df_xbrl_labels.label_string.str.contains(
                            '^流動資産$')].drop_duplicates()
    print '\n',parent,'\n' # 流動資産のelement_idを表示
    # B/Sの流動資産に関する情報のみ取得
    parent = 'jppfs_cor_currentassetsabstract'
    df_xbrl_ps_cbs = df_xbrl_presentation.ix[df_xbrl_presentation.role_id.str.contains('rol_ConsolidatedBalanceSheet'),:]
    # 再帰的に流動資産の子要素以下の要素を取得
    df_descendant = xp.gather_descendant(df_xbrl_ps_cbs,parent).dropna() # delete nan
    # 特定の勘定科目の情報のみ取得
    df_fi_cyi_caa = xp.get_specific_account_name_info(dat_fi_cyi, df_descendant)
    # ラベルと金額情報のみ表示
    print df_fi_cyi_caa[['label_string','amount']].drop_duplicates()
    
if __name__=='__main__':
    namespaces = {'link': 'http://www.xbrl.org/2003/linkbase',
              'xml':'http://www.w3.org/XML/1998/namespace',
              'xlink':'http://www.w3.org/1999/xlink',
              'xsi':'http://www.w3.org/2001/XMLSchema-instance'
              }
    main(namespaces)