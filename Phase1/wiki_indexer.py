import xml.etree.ElementTree as ET
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import *
from nltk.stem.porter import *
import pickle
import sys
import os
from collections import *
# from parse import ParseXML
def ParseXML():
	try:

		tree=ET.parse(get_InputPath())
	except:
		print("Give full path to the file")
	root=tree.getroot()
	block_text=[]
	cnt=1

	for child in root.iter():
		if child.tag=="{http://www.mediawiki.org/xml/export-0.8/}text" :
			if cnt%400==0:
				m=block_text
				block_text=deque()
				yield(m)
			block_text.append(child.text)
			cnt+=1
	yield(block_text)

			# yield(child.text)	
def Tokenize():
	tokenizer=RegexpTokenizer(r'[0-9]{4}|[a-zA-Z]{3,}')
	for docs in ParseXML():
		doc_tokens=[]
		for doc in docs:
			doc_tokens.append(tokenizer.tokenize(doc.lower()))
		yield(doc_tokens)
def getstopwordlist():
	ca=stopwords.words("english")
	ca=set(ca)
	ca.update(['amp','http','com','www','ref','web','url','deadurl','archiveDate','archiveurl',\
		'quot','accessdate','cite'])
	return ca
def StopwordsCheck():
	stopwords=getstopwordlist()
	for tokensd in Tokenize():
		p_tokens=[]
		for tokens in tokensd: 

		# p_tokens=list(filter(lambda x: x not in stopwords,tokens))
			p_tokens.append([x for x in tokens if x not in stopwords])
		# print(p_tokens)
		yield(p_tokens)
def Stemwords():
	stemmer=PorterStemmer()
	# mp=deque()
	for tokensd in StopwordsCheck():
		p_tokens=[]
		for tokens in tokensd: 
			p_tokens.append([stemmer.stem(token) for token in tokens])
		yield(p_tokens)

def saveParsedOutput():
	tokens=Stemwords()
	with open("data/docs.txt",'wb') as fp:
		pickle.dump(tokens,fp)
def readParsedOutput():
	with open("docs.txt",'rb') as fp:
		tokens=pickle.load(fp)
def MakePostinglist():
	docID=1
	vocab=defaultdict()
	word_dict=OrderedDict()
	comdict=defaultdict(list)
	count=1
	blockq=deque([])
	blockID=1
	for wordsd in Stemwords():
		comdict=defaultdict(list)
		tups=set()
		for words in wordsd:
			counter=Counter(words)
			flag=set()
			for word in words:
				# tups=[(docID,counter[word]) for word in words]
				if word not in flag:
					tfd=counter[word]
					flag.add(word)
					if word not in word_dict:
						word_dict[word]=len(word_dict)+1
					tups.add((word_dict[word],(docID,tfd)))
			docID+=1
		blockID+=1	
		tups=list(tups)
		tups.sort(key=lambda k:k[0])
			
		for _termid,_docid in tups:
			comdict[_termid].append(_docid)
		_terms=list(comdict.keys())
		_terms.sort()
		for _termid in _terms:
			comdict[_termid].sort(key= lambda k: k[0])
		filewrite(blockID,comdict)
		blockq.append(blockID)
		print("Processing block :"+str(blockID))
			
			
	# with open('data1/invertedindex.txt','wb') as fp:
	# 	pickle.dump(_plist,fp)
	print("Blocks Processed = "+str(blockID))
	MergePostingLists(blockq,docID)
	print("Merging Posting Lists done! YAY")
	# print(docID)
def MergePostingLists(blockq,docID):
	while len(blockq)>1: 
		p1=blockq.popleft()
		p2=blockq.popleft()
		with open('blockpl/'+str(p1)+'th-block-posting.txt','rb') as fp:
			plist1=pickle.load(fp)
		with open('blockpl/'+str(p2)+'th-block-posting.txt','rb') as fp:
			plist2=pickle.load(fp)
		term_id_1=list(plist1.keys())
		term_id_2=list(plist2.keys())
		comb_dict=OrderedDict()
		x,y=0,0
		while x<len(term_id_1) and y<len(term_id_2):
			_x=term_id_1[x]
			_y=term_id_2[y]
			if _x==_y:
				# MergeAndWrite(plist1[_x],plist2[_y],_x)
				# comb_dict[_x]=Merge(plist1[_x],plist2[_y],_x)
				_l=plist1[_x]+plist2[_y]
				_l.sort()
				comb_dict[_x]=_l
				x+=1
				y+=1
			elif _x<_y:
				# Write(plist1[_x],_x)
				comb_dict[_x]=plist1[_x]
				x+=1
			else:
				# Write(plist2[_y],_y)
				comb_dict[_y]=plist2[_y]
				y+=1
		while x<len(term_id_1):
			g=term_id_1[x]
			# Write(g,plist1[g])
			comb_dict[g]=plist1[g]
			x+=1
		while y<len(term_id_2):
			g=term_id_2[y]
			# Write(g,plist2[g])
			comb_dict[g]=plist2[g]
			y+=1
		# print("Merge")
		filewrite(docID+p1,comb_dict)
		blockq.append(docID+p1)
	# filewrite('InvertedIndex',comb_dict)
	if os.path.isdir(get_OutputPath()):
		with open(get_OutputPath()+'/InvertedIndex.txt','wb') as fp:
			pickle.dump(comb_dict,fp)
	else:
		with open(get_OutputPath(),'wb') as fp:
			pickle.dump(comb_dict,fp)

def filewrite(m,n):
	if not os.path.exists('blockpl'):
		os.makedirs('blockpl')
	with open('blockpl/'+str(m)+'th-block-posting.txt','wb') as fp:
		pickle.dump(n,fp)
def get_InputPath():
	return sys.argv[1]
def get_OutputPath():
	return sys.argv[2]
MakePostinglist()
