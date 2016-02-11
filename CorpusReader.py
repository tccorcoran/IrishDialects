#!/usr/bin/env python
from pdb import set_trace
from re import compile
import json
from glob import glob
class CorpusReader:
    def __init__(self,dialectChoice, limit=0):
        self.metaFiles = glob('json_files/*-meta.json')
        dia = set()

        for i in self.metaFiles:
            with open(i) as fi:
                f = json.load(fi)
            dia.add(f['dialect'])
        self.mem_limit = limit
        self.dialectList = dia
        self.dialectChoice = dialectChoice
        self.dialect = self.getDialect()
    
    def __len__(self):
        return self.countWords(self.dialect)
    def __iter__(self):
        for item in self.dialect:
            yield item
    def setMemLimit(self,limit):
        self.mem_limit = limit
    def countSentences(self):
        return sum((len(x['sentences']) for x in self.dialect))
    
    def countBooks(self):
        return len(self.dialect)

    def truncateBooks(self, minNum):
        self.dialect = self.dialect[:minNum]
    def truncateSentences(self,minNum):
        stop = self.countSentences() - minNum
        i = 0
        while self.countSentences() > minNum:
            for q in xrange(len(self.dialect)-1,-1,-1):
                if i >= stop: break
                for _ in xrange(len(self.dialect[q]['sentences'])-1,-1,-1):
                    self.dialect[q]['sentences'] = \
                            self.dialect[q]['sentences'][:-1]
                    i+=1
                    if i>= stop: break
        for q in xrange(len(self.dialect)-1,-1,-1):
            if not self.dialect[q]['sentences']:
                del self.dialect[q]

    def truncateWordList(self,minNum):
        """reduces the amount of words in dialect
        this helps to build a balanced set"""
        stop = len(self)-minNum
        i = 0
        while len(self) > minNum:
            for q in xrange(len(self.dialect)-1,-1,-1):
                if i >= stop:
                    break
                for p in xrange(len(self.dialect[q]['sentences'])-1,-1,-1):
                    i+= len(self.dialect[q]['sentences'][-1])
                    self.dialect[q]['sentences'] = \
                            self.dialect[q]['sentences'][:-1]
                    if i >= stop:
                        break
            for q in xrange(len(self.dialect)-1,-1,-1):
                if not self.dialect[q]['sentences']:
                    del self.dialect[q]
    def countWords(self, dialectList):
        return sum([len(j) for i in dialectList for j in i['sentences']])
        # means -->
        x = 0
        for i in dialectList:
            for j in i['sentences']:
                x+= len(j)
        return x
    
    def getDialect(self):
        # control for time, genre,translation
        def checkTime(j):
            if j['pubdate'].startswith('19'):
                return True
            if j['time'].startswith('19'):
                return True
            if j['time'].startswith('20'):
                return True
            if j['pubdate'].startswith('20'):
                return True
            return False
        def checkNativeSpeaker(j):
            if j['nativespeaker'] == 'yes':
                  #and j['translation'] == 'no':
                return True
            return False
        l = []
        for f in self.metaFiles:
            if len(l) > self.mem_limit and self.mem_limit: break
            with open(f) as fi:
                j = json.load(fi)
            if len(j['dialect']) == 0 : continue
            if j['dialect'].lower() in self.dialectChoice.lower() \
                    and checkTime(j) and checkNativeSpeaker(j):
                with open('json_files/'+j['doc id']+'.json') as fi:
                    l.append(json.load(fi))
        return l
            

    def makeJSONS(self,vert_file):
        i = 0
        with open(vert_file) as fi:
            
            line = fi.readline()
            for _ in xrange(39008721):
                if line.startswith('<doc id='):
                    print i
                    i+=1
                    meta = {'doc id':"", 'title':"", 'author':"", 
                        'nativespeaker':"", 
                        'dialect':"", 'medium':"", 'genre':"", 'genre2':"", 
                        'pubdate':"", 'translation':"", 'origtitle':"", 
                        'origauthor':"", 'time':"", 'authordob':"", 
                        'birthplace':"", 'residence':"", 'wordcount':""}
                    for dp in meta:
                        pat = compile(r'%s="(.*?)"'%dp)
                        meta[dp] = pat.findall(line)[0]
                    sentences = [] # all sentences in doc go here
                    line = fi.next()
                    #set_trace
                    while not line.startswith('<doc id='):
                        sentence = []   # words for a sentence go here 
                        while not line.startswith('</s>'):
                            if line.startswith('<doc id='):
                                break
                            elif line.startswith('<s>'):
                                line = fi.next()
                                break
                            else:
                                word={'token':'','POS':'','lemma':''}
                                l = line.split()
                                #set_trace()
                                if len(l) == 3:
                                    word['token'],word['POS'],word['lemma'] = l
                                    sentence.append(word)
                                    line = fi.next()
                                else:
                                    line = fi.next()
                               
                        #set_trace()
                        if not line.startswith('<doc id='):
                            try: line = fi.next()
                            except  StopIteration: break 
                        if sentence:
                            sentences.append(sentence)
#                    set_trace()
                    d = meta
                    with open(d['doc id']+'-meta.json', 'w') as fo:
                        json.dump(meta,fo)
                    d['sentences'] = sentences
                    with open(d['doc id']+'.json', 'w') as fo:
                        json.dump(d,fo)

                   # set_trace()


if __name__ == '__main__':

    c = CorpusReader()
    set_trace()    


