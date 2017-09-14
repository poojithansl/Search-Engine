import xml.etree.ElementTree as ET
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import *
from nltk.stem.porter import *
import gensim
from gensim import parsing
import pickle
import sys
import codecs
import os
from collections import *
class TokenStream:
	def __init__(self,obj):
		self.obj=obj
	def tokenize(self):
		tokenizer = RegexpTokenizer(r'[0-9]{4}|[a-zA-Z]{3,}')
		for b_docs in self.obj.parseXML():
			b_tokens=[]
			for docs in b_docs:
				doc_tokens = defaultdict(list)
				for doc in docs.keys():
					try:
						doc_tokens[doc]=tokenizer.tokenize(docs[doc].lower())
					except:
						pass
				b_tokens.append(doc_tokens)
			yield(b_tokens)
	def getstopwordlist(self):
		ca = stopwords.words("english")
		ca = set(ca)
		ca.update(['amp','http','com','www','ref','web','url','deadurl','archiveDate','archiveurl',\
			'quot','accessdate','cite','nbsp','isbn','htm','cols','category'])
		return ca
	def filter_stopwords(self):
		stopwords = self.getstopwordlist()
		for b_tokens in self.tokenize():
			p_tokens=[]
			for doc_tokens in b_tokens:
				d_tokens=defaultdict(list)
				for doc in doc_tokens.keys():
					d_tokens[doc] = list(filter(lambda x: x not in stopwords,doc_tokens[doc]))
				# print d_tokens
				# break
				p_tokens.append(d_tokens)
			yield(p_tokens)

	def stem_tokens(self):
		stemmer = PorterStemmer()
		# mp=deque()
		i=0
		for tokensd in self.filter_stopwords():
			p_tokens = []
			for tokens in tokensd: 
				d_tokens=defaultdict(list)
				for doc in tokens.keys():
					d_tokens[doc] = [gensim.parsing.stem_text(token) for token in tokens[doc]]
				
				p_tokens.append(d_tokens)
				# print i
				i+=1
			# print p_tokens
			yield(p_tokens)


class Parse:
	def __init__(self,file):
		self.file=file


	def parseXML(self):
		"""try:

			tree=ET.iterparse(self.file)
		except:
			print("Give full path to the file")"""
		# root=tree.getroot()
		flag=0
		if os.path.exists('meta.txt'):
			with open('meta.txt','rb') as fp:
				bid=int(fp.readlines()[-1])
			flag=1
                bid=0
		block_text=[]
                
                with open('Titles/count.txt','rb') as fp:
		    cnt=int(fp.readlines()[-1])
                    print cnt
                #fpp=codecs.open('Titles/'+str(cnt/5000)+'.txt','a',encoding='utf-8')
		b_id=0
		fl=0
                cnt1=1
		for _,child in ET.iterparse(self.file):
			# print child.tag
			if flag:
				if cnt/500<bid:
					cnt+=1
					continue
			if child.tag=="title":
			 	titl=child.text
			 	text=defaultdict(str)
			 	text['t']=titl
			 	fl+=1
			if child.tag=="text" :

				if cnt%5000==0:
                                        if b_id==0:
                                            cnt1=1
                                            b_id+=1
                                            m=block_text
                                            block_text=deque()
                                            print cnt,b_id
                                            g=cnt/5000
                                            #fpp=codecs.open('Titles/'+str(g)+'.txt','w',encoding='utf-8')
                                            
                                            yield(m)
                                        elif cnt!=cnt1:
				    	    m=block_text
					    block_text=deque()
					    b_id+=1
                                            cnt1=cnt
					    print cnt,b_id
                                            g=cnt/5000
                                            #fpp=codecs.open('Titles/'+str(g)+'.txt','w',encoding='utf-8')
					    # print(m[23]['t'])
				    	    # break
					    yield(m)
				if child.text!=None:
                                        #print child.text
					if child.text.startswith("#REDIRECT"):
						continue

					text=defaultdict(str)
					lines=child.text.split('\n')
                                        #s=str(cnt)+':'+text['t']
			                #fpp.write(s)	
                                        #fpp.write('\n')
                                        # print lines
					i=0
					while i < len(lines):
						if lines[i].startswith("{{Infobox"):
							i_text=''
							k=i
							try:
								while lines[k]!='}}':
									i_text=lines[k]+' '+i_text
									k+=1
								i=k
							except:
								pass
							text['i']=i_text

						elif lines[i].startswith("==References"):
							k=i
							r_text=''
							while True:
						  
								if not lines[k].startswith('*'):
									break
								r_text=lines[k]+' '+r_text
								k+=1
							i=k
							text['r']=r_text
						elif lines[i].startswith("==External links"):
							k=i
							l_text=''
							while True:
						  
								if not lines[k].startswith('*'):
									break
								l_text=lines[k]+' '+l_text
								k+=1
							i=k
							text['l']=l_text
						elif lines[i].startswith("[[Category"):
							k=i
							c_text=''
							try:
								while lines[k].startswith("[[Category"):
									c_text=lines[k]+' '+c_text
									k+=1
									i=k
							except:
								pass
							text['c']=c_text
						else:
							text['b']=lines[i]+' '+text['b']
						i+=1
					# print(text)
					# break
					block_text.append(text)
					cnt+=1
                                        if cnt%1000==0:
                                            print cnt
                                            sys.stdout.flush()
		yield(block_text)

Parsefile=Parse('../../../Data/wiki-search-small.xml')
# Parsefile.parseXML()
ts=TokenStream(Parsefile)
ts.stem_tokens()
