import os
import files.porter as porter
import math
import re
import time
from optparse import OptionParser

#claim a stemmer
stemmer = porter.PorterStemmer()

freqs = {} # key(doc id), value(key--term, value-appear times)
lengths = {} # key(doc id), value(length)
#docn_times = {} # key(term), value(the total number of docs in the collection that contain term k)
term_docs = {} # key(term), value(a list contains all the id of docs contain it)
avg_doclen = 0 # average length of the doc in the collection

# read the stopwords files and store them into a set
with open('./files/stopwords.txt', 'r') as f:
    stopwords = set(f.read().split())

# This funstion is used to read the index stored before
def readin_index():
    global freqs, lengths, term_docs, avg_doclen

    with open('corpus-large', 'r', encoding='UTF-8') as f:

        file_part = 1 # this file has totally four parts, this variable is the index
        term_freqs = {} # key(term), value(term frequncy)
        doc_id = -1
        for line in f:
            
            line = line.split()
            if line[-1] == '-----':
                if file_part == 1:
                    freqs[doc_id] = term_freqs
                file_part += 1
                continue

            if file_part == 1:
                
                if len(line) == 1:
                    if doc_id != -1:
                        freqs[doc_id] = term_freqs
                    doc_id = line[-1]
                    term_freqs = {}
                else:
                    term_freqs[line[0]] = int(line[-1])

            elif file_part == 2:
                lengths[line[0]] = int(line[-1])

            elif file_part == 3:
                term_docs[line[0]] = line[1:]

            else:
                avg_doclen = float(line[-1])

# The first time run the program needs use this function to create an index
def create_index():
    global freqs, lengths, term_docs, avg_doclen

    files = os.listdir('./documents')# get the list of files name

    documents = {} #key(doc id), value(list of word)

    for file in files: # read all the files
        with open('./documents/'+file, 'r', encoding='UTF-8') as f:
        #with open('./test/'+file, 'r') as f:
            stan = f.read()
            stan = re.sub(r'[\~|`|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=|\||\|\[|\]|\{|\}|\;|\:|\"|\'|\,|\<|\.|\>|\/|\?]',"",stan)
            documents[file] = stan.split()


    cache = {} # key(term), value(term stemmed)
    

    for did in documents:
        freq = {} # key(term), value(appear times)
        length = 0
        for term in documents[did]:
            term = term.lower()
            if term not in stopwords:
                length += 1
                if term not in cache:
                    cache[term] = stemmer.stem(term)
                term = cache[term]

                if term not in freq: # first appear in this doc
                    freq[term] = 1
                    if term not in term_docs: # operate term_docs
                        term_docs[term] = list()
                    term_docs[term].append(did)

    #                if term not in docn_times: # operate docn_times
    #                    docn_times[term] = 1
    #                else:
    #                    docn_times[term] += 1
                else:
                    freq[term] += 1

        freqs[did] = freq
        lengths[did] = length
        avg_doclen += length

    avg_doclen /= len(freqs)



    # store the data handled into an index file
    with open('corpus-large','w+', encoding='UTF-8') as f:
        for doc_id in freqs: # store the 'freqs' dictionary
            f.write(str(doc_id)+'\n')
            for term in freqs[doc_id]:
                f.write(term+" "+str(freqs[doc_id][term])+'\n')
               
        f.write('-----\n') # split line

        for doc_id in lengths: # store the 'lengths' dictionary
            f.write(str(doc_id)+" "+str(lengths[doc_id])+'\n')
        
        f.write('-----\n') # split line

        for term in term_docs: # store the 'term_docs' dictionary
            f.write(term+" ")
            for doc_id in term_docs[term]:
                f.write(doc_id+" ")
            f.write('\n')

        f.write('-----\n') # split line

        f.write(str(avg_doclen)) # store the value of average length of the collection

# create output.txt file
def create_large_output():
    global freqs, lengths, term_docs, avg_doclen
    querys = {} # key(query id), value(list of terms in this query)

    if os.path.exists('corpus-large'): # not the first times
        readin_index()
    else:# the first running 
        create_index()
        
    #query access
    with open('./files/queries.txt', 'r', encoding='UTF-8') as f:
        for line in f:
            line = re.sub(r'[\~|`|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=|\||\|\[|\]|\{|\}|\;|\:|\"|\'|\,|\<|\.|\>|\/|\?]',"",line)
            query = line.split()
            querys[query[0]] = query[1:]



    sims = {} # key(query id), value(key--document id, value--similarity score)


    for quid in querys:
        
        sim = {} # key(document id), value(similarity score)
        for term in querys[quid]:
            
            term = term.lower()
            
            if term not in stopwords:
                term = stemmer.stem(term)
                
                if term in term_docs:
                    
                    for doc_id in term_docs[term]:
                        sim_value = freqs[doc_id][term] * (1 + 1) / ( freqs[doc_id][term] + 1 * ( (1-0.75) + ( 0.75 * lengths[doc_id]/avg_doclen) ) )
                        sim_value *= math.log( (len(freqs)-len(term_docs[term])+0.5)/(len(term_docs[term])+0.5), 2 )
                        
                        if doc_id not in sim:
                            sim[doc_id] = sim_value
                        else:
                            sim[doc_id] += sim_value 
        sims[quid] = sim
    
    #create output.txt file
    with open('output.txt','w') as f:
        index = 0
        for quid in sims:
            index = 1
            for did in sorted( sims[quid], key=sims[quid].get, reverse=True):
                if sims[quid][did] > 0:
                    f.write(quid+" "+"Q0"+" "+did+" "+str(index)+" "+str(sims[quid][did])+" "+"17206176\n")
                    index += 1
                if index > 50:
                    break

# this function respose the command '-m manual', used for user input
def get_user_input():
    global freqs, lengths, term_docs, avg_doclen
    print('Loading BM25 index from file, please wait')
    if os.path.exists('corpus-large'): # not the first times
        readin_index()
    else:# the first running 
        create_index()

    print('please enter your query:')
    while(True):
        user_input = input()
        if user_input == 'QUIT':
            break
        else:
            sim = {} # key(document id), value(similarity score)
            
            query = re.sub(r'[\~|`|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=|\||\\|\[|\]|\{|\}|\;|\:|\"|\'|\,|\<|\.|\>|\/|\?]',"",user_input)
            query = query.split()

            for term in query:
                term = term.lower()
                if term not in stopwords:
                    term = stemmer.stem(term)

                    if term in term_docs:
                
                        for doc_id in term_docs[term]:
                            sim_value = freqs[doc_id][term] * (1 + 1) / ( freqs[doc_id][term] + 1 * ( (1-0.75) + ( 0.75 * lengths[doc_id]/avg_doclen) ) )
                            sim_value *= math.log( (len(freqs)-len(term_docs[term])+0.5)/(len(term_docs[term])+0.5), 2 )
                            
                            if doc_id not in sim:
                                sim[doc_id] = sim_value
                            else:
                                sim[doc_id] += sim_value
            index = 1
            if sim:
                for did in sorted( sim, key=sim.get, reverse=True)[:15]:
                    print(str(index)+" "+did+" "+str(sim[did]))
                    index += 1
            else:
                print('no relevant documents')


rel_qrels = {} # key(query id), value( key--document id, value--relevance)      
result = {} # key(query id(int)), value(a list store all the doc_id)            
relret = {} # key(query id), value(a list store all the doc_id in both set)     
unrel_qrels = {} # key(query id), value(set of unrelevant doc)

# get the rel collection from the exsiting file
def getRel_qrels():
    global rel_qrels, unrel_qrels

    query_id = 700 # it is the query id 
    rel_doc = {} # key(doc id), value(relevance)
    unrel_doc = set() # store all the unrelevant doc for one query
    with open('./files/qrels.txt','r', encoding='UTF-8') as f:
        for line in f:
            items = line.split()
            if items[0] != query_id:
                if query_id != 700:
                    if rel_doc:
                        rel_qrels[query_id] = rel_doc
                    if unrel_doc:
                        unrel_qrels[query_id] = unrel_doc
                query_id = items[0]
                rel_doc = {}
                unrel_doc = set()
            if int(items[-1]) <=0:
                unrel_doc.add(items[-2])
            else:
                rel_doc[items[-2]] = items[-1]
        if rel_doc:        
            rel_qrels[query_id] = rel_doc
        if unrel_doc:
            unrel_qrels[query_id] = unrel_doc


def getRet():
    global result, relret, rel_qrels
    
    with open('output.txt','r', encoding='UTF-8') as f:
        quid = '701'
        shar_ids = [] # all the doc id in both rel and res
        res_ids = [] # after we will use rank position, so I use list to store result doc id
        for line in f:
            line = line.split()
            
            if int(line[0]) == quid:
                res_ids.append(line[2])
            else:
                result[str(quid)] = res_ids
                res_ids = []
                res_ids.append(line[2])
                if shar_ids:
                    relret[str(quid)] = shar_ids
                shar_ids = []
                quid = int(line[0])

            if str(quid) in rel_qrels:
                if line[2] in rel_qrels[str(quid)]:
                    shar_ids.append(line[2])
        result[str(quid)] = res_ids
        if shar_ids:
            relret[str(quid)] = shar_ids

# calculate precision
def Precision():
    precision = {} # key(the query id), value(the precision value)
    avg_precision = 0 # the average value of all the query precision value
    for qid in relret:
        precision[qid] = len(relret[qid]) / len(result[str(qid)]) 
        avg_precision += precision[qid]
    print("{0:15}".format('Precision:'),end='')
    print(avg_precision/len(precision))

# calculate recall
def Recall():
    recall = {} # key(the query id), value(the Recall value)
    avg_recall = 0 # the average value of all the query recall value
    for qid in rel_qrels:
        if qid in relret:
            recall[qid] = len(relret[qid]) / len(rel_qrels[str(qid)])
            avg_recall += recall[qid]
    print("{0:15}".format('Recall:'),end='')
    print(avg_recall/len(recall))

# calculate P@n
def Precision_n(n):
    Precision_n = {} # key(the query id), value(the Precision at n)
    avg_precision_n = 0 # the average value of all the query precision_10 value 
    for qid in result:
        i = 0 # current number of documents 
        value = 0 # current number of relevant documents
        for did in result[qid]:
            i += 1
            if i == (n+1):
                break
            if qid in rel_qrels:
                if did in rel_qrels[qid]:
                    value += 1
            else:
                break
        value /= n
        Precision_n[qid] = value
        avg_precision_n += Precision_n[qid]
    
    print("{0:15}".format('P@10:'),end='')
    print(avg_precision_n/len(Precision_n))

# calculate R_precision
def R_precision():
    R_precision = {} # key(the query id), value(the R-precision)
    avg_R_precision = 0 # the average value of all the query R_precision value 
    for qid in result:
        i = 0 # avoid out of boundary
        value = 0 # current number of relevant documents
        if qid in rel_qrels:
            for did in range(len(rel_qrels[qid])):
                if i == len(rel_qrels[qid]) or i >= len(result[qid]):
                    break
                if result[qid][did] in rel_qrels[qid]:
                    value += 1
                i += 1
            
            R_precision[qid] = value / len(rel_qrels[qid])
            avg_R_precision += R_precision[qid]
    
    print("{0:15}".format('R_precision:'),end='')
    print(avg_R_precision/len(R_precision))

# calculate map
def Map():
    map_value = 0 # the value of Map  
    real_times = 0 
    for quid in result:
        rel = 0 # current relevant documents number
        doc_num = 0 # AP for one query
        v = 0 # current documents number
        if quid in rel_qrels and quid in relret:
            real_times += 1
            for did in result[quid]:
                doc_num += 1
                
                if did in relret[quid]:
                    rel += 1 
                    v += rel / doc_num
            map_value += (v/len(rel_qrels[quid]))
    map_value /=  real_times
    print("{0:15}".format('Map:'),end='')
    print(map_value)
    
# calculate bpref
def bpref():
    bprefs = {} # key(query id), value(bref value)
    avg_bprefs = 0 # the average value of all the query brpef value 
    for quid in result:
        n_rel_num = 0
        bref_v = 0 # the value of bref for one ruery
        if quid in rel_qrels:
            for did in result[quid]:
                if did in unrel_qrels[quid]:
                    if n_rel_num < len(rel_qrels[quid]):
                        n_rel_num += 1
                    else: 
                        break
                elif did in rel_qrels[quid]:
                    v = 1 - n_rel_num/len(rel_qrels[quid])
                    bref_v += v
            bref_v /= len(rel_qrels[quid])
            bprefs[quid] = bref_v
            avg_bprefs += bprefs[quid]
    print("{0:15}".format('bpref:'),end='')
    print(avg_bprefs/len(bprefs))

# evaluation function
def evaluation():
    create_large_output()
    getRel_qrels()
    getRet()

    print("{0:15}{1:10}".format('Evaluation','result'))
    Precision()
    Recall()
    Precision_n(10)
    R_precision()
    Map()
    bpref()



start_time = time.process_time()


evaluation()

# # create an object of OptionParser
# parser = OptionParser()
# # add parameter in to OptionParaser object
# parser.add_option('-m',type='string')
# # get parameter value
# options, args = parser.parse_args()


# # according to differnt parameter run the differnt function
# if options.m == 'manual':
#     get_user_input()

# if options.m == 'evaluation':
#     evaluation()




end_time = time.process_time()
print( 'Time is {} seconds'.format( end_time - start_time ) )