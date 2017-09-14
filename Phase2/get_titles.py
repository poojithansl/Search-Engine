# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import *
from nltk.stem.porter import *
import gensim
from gensim import parsing
import pickle
import sys
import os
from collections import *
import codecs
def parse(file):
	
	if not os.path.exists('Titles'):
		os.makedirs('Titles')
        with open('Titles/count.txt','rb') as fp:
            offset=int(fp.readlines()[-1])
	cnt=offset
        cnt1=0
        fp=codecs.open('Titles/'+str(offset/10000)+'.txt','ab',encoding='utf-8')
	for _,child in ET.iterparse(file):
		if child.tag=="title":
			title=child.text
			# text=defaultdict(str)	
		if child.tag=="text":
			if child.text!=None and not child.text.startswith("#REDIRECT"):
				if cnt%10000==0:
                                        if cnt1!=cnt:
					    g=cnt/10000
                                            cnt1=cnt
					    fp=codecs.open('Titles/'+str(g)+'.txt','ab',encoding='utf-8')
                                            print cnt

                                #print cnt,title
                                s = str(cnt)+':'+title
                                try:
                                    #print(s)
                                    fp.write(s)
                                    fp.write('\n')
                                except UnicodeEncodeError:
                                    print s
                                    pass
                                cnt+=1
        return cnt

cnt=parse(sys.argv[1])
print cnt
with codecs.open('Titles/count.txt','a',encoding='utf-8') as fp:
	fp.write(str(cnt)+'\n')
