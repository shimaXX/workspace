
import imtools
import sift
import os

imlist = imtools.get_imlist('nail_book03')
nbr_images = len(imlist)
featlist = [ imlist[i][:-3]+'sift' for i in range(nbr_images)]

for i in range(nbr_images):
    flug = os.path.exists("./"+ featlist[i])
    if flug:
        print "exist ",featlist[i]
        continue
    else: sift.process_image(imlist[i],featlist[i])
