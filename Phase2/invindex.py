from tokenp import *
from collections import *
import codecs
import os
import sys
import json
class Block:
	def __init__(self,block_ID):
		self.block_ID=block_ID

	def create_postings(self,op,flag=1):
		tups=defaultdict(dict)
		blockq=deque([])
                docID=0
                with open('Titles/count.txt','rb') as fp:
		    docID=int(fp.readlines()[-1])-1
                
		if flag:
			with open('large_index/dictionary.json','rb') as fp:
				word_dict=json.load(fp)
                                print "word_dict loaded"
		else:
			word_dict=defaultdict(list)
		
		# block_ID=0
		for words in op.stem_tokens():
			self.block_ID+=1
			tups=defaultdict(dict)
			for words_doc in words:
				docID+=1
				st=''
				tfd=0
				for tag in words_doc.keys():
					counter=Counter(words_doc[tag])
					flag=set()
					for word in words_doc[tag]:
						if word not in flag:
							flag.add(word)
							tfd2=counter[word]
							st=tag+':'+str(tfd2)
							if word not in word_dict:
								word_dict[word].append(len(word_dict)+1)
							if docID not in tups[word_dict[word][0]].keys():
								tups[word_dict[word][0]][docID]=[tfd2,st]
								word_dict[word].append(1)
							else:
								tups[word_dict[word][0]][docID][0]+=tfd2
								word_dict[word][1]+=1
								tups[word_dict[word][0]][docID][1]+=st
			# print(tups.keys())
			store_postings(tups,self.block_ID)
			# if self.block_ID%2==0:
			# 	print self.block_ID
			meta_file=open('meta.txt','wb')
			meta_file.write(str(self.block_ID))
			meta_file.close()
			blockq.append(str(self.block_ID))
		if not os.path.exists('large_index'):
			os.makedirs('large_index')
		with open('large_index/dictionary.json','wb') as fp:
			json.dump(word_dict,fp)
                print docID,self.block_ID
		return blockq
				# tups.add(word_dict[word],(docID,tfd,st))

def store_postings(tups,block_ID):
	if not os.path.exists('blockpl'):
		os.makedirs('blockpl')
	with open('blockpl/'+str(block_ID)+'.txt','wb') as fp:	

		for key in tups.keys():
			m=str(key)+'-'
			kiks=tups[key].keys()
			g=str(kiks[0])+'.'+str(tups[key][kiks[0]][0])+'.'+str(tups[key][kiks[0]][1])
			for did in kiks[1:]:
				g=g+';'+str(did)+'.'+str(tups[key][did][0])+'.'+str(tups[key][did][1])

			fp.write(m+g+'\n')

def Merge_blocks(blockq):
	while len(blockq)>1:
		p1=blockq.popleft()
		p2=blockq.popleft()
		file1=open('blockpl/'+p1+'.txt','rb')
		file2=open('blockpl/'+p2+'.txt','rb')
		line1=file1.readline().strip('\r\n')
		line2=file2.readline().strip('\r\n')
		m_str=''
		fl=0
		if len(blockq)==0:
			if not os.path.exists('large_index'):
				os.makedirs('large_index')
			m_file=open('large_index/Inverted_index.txt','wb')
		else:
			m_file=open('blockpl/'+'m-'+str(p1)+'.txt','wb')
			fl=1
			# 
			
		while line1 and line2:
			try:
				# if '-' in line1:
				id1,pl1=line1.split('-')
				# if '-' in line2:
				id2,pl2=line2.split('-')
			except:
				print line1,line2
			id1,id2=int(id1),int(id2)
			if id1==id2:
				pl=pl1+';'+pl2
				m_file.write(str(id1)+'-'+pl+'\n')
			elif id1<id2:
				pl=pl1
				m_file.write(str(id1)+'-'+pl+'\n')
			elif id2<id1:
				pl=pl2
				m_file.write(str(id2)+'-'+pl+'\n')
			# check(m_str)
			line1=file1.readline().strip('\r\n')
			line2=file2.readline().strip('\r\n')
		while line1:
			m_file.write(line1+'\n')
			line1=file1.readline().strip('\r\n')
		while line2:
			m_file.write(line2+'\n')
			line2=file2.readline().strip('\r\n')
		# m_file.write(m_str)
		if fl:
			blockq.append('m-'+str(p1))
			

# 	def get_docs():
bid=0
flag=0
if os.path.exists('meta.txt'):
	with open('meta.txt','rb') as fp:
		bid=int(fp.readlines()[-1])
		flag=0
b=Block(0)
# Parsefile=Parse('../../../Data/wiki-search-small.xml')
Parsefile=Parse(sys.argv[1])

# Parsefile=Parse('../../Phase1/201402182/ire-2017/enwiki-20170820-pages-articles15.xml')

# Parsefile.parseXML()
ts=TokenStream(Parsefile)
bq=b.create_postings(ts,flag)

# bq=deque([])
# for i in range(1,bid+1):
# 	bq.append(str(i))
# Merge_blocks(bq)
