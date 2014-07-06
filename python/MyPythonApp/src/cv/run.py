# coding: utf8
'''
Created on 2013/04/04

@author: n_shimada
'''
import harris
import sift
import numpy as np
from PIL import Image
from pylab import *
import os
import urllib
import urllib3, urlparse
import simplejson as json
#import pydot

inpfilename = 'C:/workPyth/MyPython/cv/data/empire.jpg'
outpfilename = 'C:/workPyth/MyPython/cv/result.pgm'
def coner():
    im = np.array(Image.open(inpfilename).convert('L'))
    harrisim = harris.compute_harris_response(im)
    filtered_coords = harris.get_harris_points(harrisim,6)
    harris.plot_harris_points(im, filtered_coords)

def cof():
    im1 = np.array(Image.open(inpfilename).convert('L'))
    im2 = np.array(Image.open(inpfilename).convert('L'))
    wid = 5
    harrisim = harris.compute_harris_response(im1,5)
    filtered_coords1 = harris.get_harris_points(harrisim, wid+1)
    d1 = harris.get_descriptors(im1, filtered_coords1,wid)
    
    harrisim = harris.compute_harris_response(im2,5)
    filtered_coords2 = harris.get_harris_points(harrisim, wid+1)
    d2 = harris.get_descriptors(im2, filtered_coords2,wid)
    
    print 'starting matching'
    matches = harris.match_twosided(d1,d2)
    print "matches", matches
    
    figure()
    gray()
    harris.plot_matches(im1, im2, filtered_coords1, filtered_coords2, matches)
    print "show the image"
    show()

def panoramio():
    # 画像を問い合わせる
    url = 'http://www.panoramio.com/map/get_panoramas.php?order=popularity&\
    set=public&from=0&to=20&minx=-77.037564&miny=38.896662&\
    maxx=-77.035564&maxy=38.898662&size=madium'
    c = urllib.urlopen(url)
    
    # JSONから各画像のURLを取り出す
    j = json.loads(c.read())
    imurls = []
    for im in j['photos']:
        imurls.append(im['photo_file_url'])
        
    # 画像をダウンロードする
    for url in imurls:
        image = urllib.URLopener()
        image.retrieve(url, os.path.basename(urlparse.urlparse(url).path))
        print 'downloading:', url

def _match():
    imlist = []
    featlist = []
    nbr_image = len(imlist)
    
    matchscores = zeros((nbr_images, nbr_images))
    
    for i in xrange(nbr_images):
        for j in xrange(i, nbr_image): # 上三角成分だけを計算する
            print 'comparing', imlist[i], imlist[j]
            
            l1, d1 = sift.read_features_from_file(featlist[i])
            l2, d2 = sift.read_features_from_file(featlist[j]) 
            
            matches = sift.match_twosided(d1, d2)
            
            nbr_matches = sum(matches > 0)
            print 'number or matches = ', nbr_matches
            matchscores[j,i] = nbr_matches
        
    # 値をコピーする
    for i in xrange(nbr_images):
        for j in xrange(i+1, nbr_images): # 対角成分はコピー不要
            matchscores[j,i] = matchscores[i,j]

def glaph():
    g = pydot.Dot()
    
    g.add_node(pydot.Node(str(0), fontcolor='transparent'))
    for i in xrange(5):
        g.add_node(pydot.Node(str(i+1)))
        g.add_edge(pydot.Edge(str(0),str(i+1)))
        for j in xrange(5):
            g.add_node(pydot.Node(str(j+1) +'-'+str(i+1)))
            g.add_edge(pydot.Edge(str(j+1) +'-'+str(i+1), str(j+1)))
    g.write_png('graph.jpg', prog='neato')

def glaph_thumb():
    threshold = 2 # リンクを作成するのに必要な一致数
    g = pydot.Dot(graph_type='graph') # デフォルトの方向月グラフは不要
    for i in xrange(nbr_images):
        for j in xrange(i+1, nbr_images):
            if matchsrores[i,j] > threshold:
                # 組のうちの第1の画像
                im = Image.open(imlist[i])
                im.thumbnail((100,100))
                filename = str(i) + '.png'
                im.save(filename) # サムネイルをファイルに保存
                g.add_node(pydot.Node(str(i), fontcolor= 'transparent',
                        shape='rectangle', image=path+filename))
                
                # 組のうちの第2の画像
                im = Image.open(imlist[j])
                im.thumbnail((100,100))
                filename = str(j) + '.png'
                im.save(filename) # サムネイルをファイルに保存
                g.add_node(pydot.Node(str(j), fontcolor='transparent',
                        shape='rectangle', image=path+filename))
                
                g.add_edge(pydot.Edge(str(i),str(j)))
                
    g.write_png('whitehouse.png')

if __name__ == "__main__":
    #sift.process_image(inpfilename, outpfilename)
    panoramio()
    #glaph()