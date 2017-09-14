from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import *
import os
from gensim import parsing
import json
from nltk.stem.porter import *
from collections import *
import gensim
import math
import time
import heapq
N=5418847 #Number of Docs

def get_tt(query):
    a=[]
    try:
        tokenizer = RegexpTokenizer(r'[I,B,L,T,R,C,i,b,l,t,r,c]:[[a-zA-Z]{3,}|[0-9]{4}]|[a-zA-Z]{3,}|[0-9]{4}')
    except:
        print "Tags can be i,b,l,t,r,c or I,B,L,T,R,C"
    l_term=tokenizer.tokenize(query)
#     print l_term
    tag = None
    for k in l_term:
        if ':' in k:
            tag,term=k.split(':')
            a.append((tag,term))
        else:
            term=k
            a.append((tag,term))
    return a

def get_preprocessed(query):
    for tag,term in get_tt(query):
        tag=tag.lower()
        term=preprocess_field(term)
        if term==-1:
            continue
        yield(tag,term)


def preprocess_field(term):
    stopwords = getstopwordlist()
    term= -1 if term in stopwords else term
    if term!=-1:
        term=gensim.parsing.stem_text(term)
    return term

def getstopwordlist():
    ca = stopwords.words("english")
    ca = set(ca)
    ca.update(['amp','http','com','www','ref','web','url','deadurl','archiveDate','archiveurl',\
            'quot','accessdate','cite','nbsp','isbn','htm','cols','category'])
    return ca

    
def preprocess_query(query):
    tokenizer = RegexpTokenizer(r'[0-9]{4}|[a-zA-Z]{3,}')
    q_tokens=tokenizer.tokenize(query.lower())
    stopwords = getstopwordlist()
    q_tokens=list(filter(lambda x: x not in stopwords,q_tokens))
    q_tokens=[gensim.parsing.stem_text(token) for token in q_tokens]
    return q_tokens


def get_plist(i,term_id,n,tag):
    try:
	fp=open('large_index/'+str(i+1)+'/'+str(term_id[0]/n)+'.txt','rb')
	lines=fp.readlines()

	p_list=lines[term_id[0]%n]
	w_id,p_list=p_list.split('-')
	doc_record=p_list.split(';')
	for record in doc_record:
		docID,tf,f_info=record.split('.')

		if tag and tag in f_info:

			pattern = re.compile("([a-zA-Z])+:([0-9]+)")
			field=zip(*pattern.findall(f_info))
			indf=field[0].index(tag)
			tf=int(field[1][indf])

			if not int(docID) in scores:
				scores[int(docID)]=0
			tfterm,idfterm=1+tf,term_id[1]/(N*1.0)
			scores[int(docID)]+=math.log(tfterm) * math.log(idfterm)

		elif not tag:
			if not int(docID) in scores:
				scores[int(docID)]=0
			tfterm,idfterm=1+int(tf),term_id[1]/(N*1.0)
			scores[int(docID)]+=math.log(tfterm) * math.log(idfterm)

    except:
        pass

def print_titles(d_id):
        j=[]
        m=1
	for idd in d_id:
	    g=int(idd/10000)
            try:
	        fp=open('Titles/'+str(g)+'.txt','rb')
            except:
                continue
	    cnt=0
            
            line=fp.readline().strip('\r\n')
            #print 1
            while line:
	        if cnt==idd%10000:
	            
	            title=line.split(':')[1]
	            #print title
                    j.append(title)
	            break
	        line=fp.readline().strip('\r\n')
	        cnt+=1
            m+=1
            if m==k+1:
                break
        print j
        

def get_dictionary():
    for i in range(1,11):
        with open('important/dictionary'+str(i)+'.json','rb') as fp:
            voc_list.append(json.load(fp))
            #print i



n=1000
start=time.time()
voc_list=[]
get_dictionary()
end=time.time()
print end-start
Query=raw_input("Please Enter the Query\n")
k=input("Enter k, the top results\n")
while Query:
        #try:
        start=time.time()
	scores=defaultdict()
	if ':' in Query:
		for tag,term in get_preprocessed(Query):
			for i,voc in enumerate(voc_list):
                                try:
                                    t_id=voc[term]
		                    p_list=get_plist(i,t_id,n,tag)
                                except:
                                    print "term not in dictionary"
                                    pass

		       
	else:
		tokens=preprocess_query(Query)
		scores=defaultdict()
		for term in tokens:
			for i,voc in enumerate(voc_list):
                            try:
				t_id=voc[term]
				get_plist(i,t_id,n,None)
                            except:
                                print "term not in dictionary"
                                pass
	# ls = list(map(lambda x: list(reversed(x)), scores.items()))
	# scrs, ids = list(zip(*heapq.nlargest(k,ls)))
        try:
	    ids,_=zip(*heapq.nlargest(k+6,scores.items(), key=lambda x: x[1]))
            #print ids
	    print_titles(ids)
        except: 
            pass
	end=time.time()
	print end-start
        #except:
        Query=raw_input("Please Enter the Query\n")
        if Query=="Quit":
            break
        k=input("Enter k, the top results\n")

