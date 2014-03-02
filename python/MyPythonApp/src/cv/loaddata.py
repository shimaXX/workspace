import pickle
import imtools
import imagesearch

with open('ukbench_imlist.pkl','rb') as f:
  imlist = pickle.load(f)
  featlist = pickle.load(f)

with open('vocabulary.pkl', 'rb') as f:
  voc = pickle.load(f)

