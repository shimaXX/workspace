# coding: utf-8
'''
Created on 2014/02/16

@author: nahki
'''
import io
from normalizewords import Transform, Replace

ifpath = 'D:/workspace/python/MyPythonApp/works/output/asumama.txt'
ofpath = 'D:/workspace/python/MyPythonApp/works/output/0216khcoder.txt'

broad_date_list = ['2014-02-10', '2014-02-14', '2014-02-15', '2014-02-16']
START = u'00:30:00' # ツイート取得開始時間
END = u'23:30:00' # ツイート取得終了時間

TIME_SPAN = 5 # ツイートの集計間隔


with open(ifpath, 'r', 1000) as inpf:
    of = io.open(ofpath, 'w')
    
    # 現在の時間タグ(year, month, day, hour, minute)
    n_ytag=''; n_mtag=''; n_dtag=''; n_htag = ''; n_mtag = ''
    for line in inpf:
        print line
        # 空行は飛ばす
        if line=='\n': continue
        
        tid, dtime, aid, text = line.strip().split('\t')
        ymd, time = dtime.split(' ')
        if ymd in broad_date_list and START <= time <= END:
            year, month, day = ymd.split('-')
            
            # <H1>タグをyearとして、年が変わる場合はタグを打つ
            if year !=  n_ytag:
                s = u'<H1>'+ Transform.tf_cnvk(year) + u'</H1>\n'
                of.write(s + u'\n')
                n_ytag = year
                
            # <H2>タグをmonthとして、月が変わる場合はタグを打つ
            if month !=  n_mtag:
                s = u'<H2>'+ Transform.tf_cnvk(month) + u'</H2>\n'
                of.write(s + u'\n')
                n_mtag = month

            # <H3>タグをdayとして、日が変わる場合はタグを打つ
            if day !=  n_dtag:
                s = u'<H3>'+ Transform.tf_cnvk(day) + u'</H3>\n'
                of.write(s + u'\n')
                n_dtag = day

            hour, minit, second = time.split(':')
            # <H4>タグをhourとして、日が変わる場合はタグを打つ
            if hour !=  n_htag:
                s = u'<H4>'+ Transform.tf_cnvk(hour) + u'</H4>\n'
                of.write(s + u'\n')
                n_htag = hour
            
            tag = '%02d' %( ( int(minit) % TIME_SPAN )*TIME_SPAN )
            if tag != n_mtag:
                tmp = ymd + u'＿' + hour + u'：' + tag
                tmp = Transform.tf_cnvk(tmp)
                s = u'<H5>'+ tmp + u'</H5>\n'
                n_mtag = tag
            else:
                s = ''
                
            # hashtagとurlを取り除く
            # 英字を大文字に統一
            # 全ての文字を大文字にする処理を加える
            text = Replace.url_replace(text)
            s += Transform.tf_cnvk( Replace.hash_replace(text.upper()) )
            
            of.write(s + u'\n')