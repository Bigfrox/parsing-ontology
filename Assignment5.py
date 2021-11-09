"""
Assignment 5, Parsing Big Data
2016253072 명수환

"""


from datetime import datetime
from os import error, name
import sys


def getDataFromFile(filename):
    file = open(filename, 'r')
    

    ontology_MF = dict()
    ontology_BP = dict() 

    line = None
    line = file.readline()
    #print(line)
    while line != "":
        #print(line)
        while (line != "[Term]\n"):
            line = file.readline() #* Term 단위
            if line == "":
                return ontology_MF,ontology_BP

        line = file.readline().split()

        #* Read line after "[Term]\n"
        if line[0] == "id:":
            id = line[1]
            #print("id:",id)
            line = file.readline().split()

        if line[0] == "name:":
            #print("name:",line[1:])
            line = file.readline().split()

        if line[0] == "namespace:":
            namespace = line[1]
            #print("namespace:",namespace)#* molecular_function,biological_process
            line = file.readline().split()

        
        is_a_relation = set()
        part_of_relation = set()
        
        while line[0] != "is_a:" and line[0] != "is_obsolete:":
            line = file.readline().split()
            
            if not line:
                break

        if not line:
            pass
        elif line[0] == "is_obsolete:":
            if line[1] == "true":
                #print(id,"is obsolete")
                continue
        elif line[0] == "is_a:":
            is_a_relation.add(line[1])
            line = file.readline().split()
        
            if line:
                while line[0] == "is_a:": #* 연속해서 relationship이 기술될 경우
                    is_a_relation.add(line[1])
                    #print(line)
                    line = file.readline().split()
                    if not line:
                        break
        
        if line:
            if line[0] == "relationship:":
                if line[1] == "part_of":
                    part_of_relation.add(line[2]) #* id
                    #print("part of : ",line[2])
                    line = file.readline().split()
                    
                    if line:
                        while line[0] == "relationship:" and line[1] == "part_of":
                            part_of_relation.add(line[2])
                            #print("part of : ",line[2])
                            line = file.readline().split()
                            if not line:
                                break

        error_relation = is_a_relation.intersection(part_of_relation)
        if error_relation:
            print(id,"has two relationship - ",error_relation)

        #* Classify - BP,MF
        if namespace == "molecular_function":
            ontology_MF[id] = list(is_a_relation.union(part_of_relation)) #* {id:relation}
        elif namespace == "biological_process":
            ontology_BP[id] = list(is_a_relation.union(part_of_relation))

        #print("BP:",ontology_BP)
        #print("MF",ontology_MF)
        

    return ontology_MF,ontology_BP


def getTermDepth(ontology,start_node,root_node):
    shortestPathLength = -1 #* 초기값
    
    
    for v in ontology[start_node]:
        edges_count = 0
        parent = v
        #print("parent : ", parent)
        edges_count += 1
        if parent != root_node:
            start_node = parent
            edges_count += getTermDepth(ontology,start_node,root_node)
        else: #* parent is root
            #print("root에서 1을 반환합니다.")
            return 1
        #print("short: ",shortestPathLength)
        #print("edge count : ",edges_count)
        if shortestPathLength != -1:
            if edges_count < shortestPathLength:
                shortestPathLength = edges_count
        elif shortestPathLength == -1:
            shortestPathLength = edges_count
        else: #* shortestPathLength < edges_count
            pass
        
    #print("short: ",shortestPathLength)
    return shortestPathLength
        
def output_to_file(filename,start_node,length):
    file = open(filename, 'a')
    

    file.write('{0} : {1}'.format(start_node,length))
        
    file.write("\n")
        

    file.close()
    #print("Finished to print to output file : ", filename)

def main():
    """
    - The number of terms: How many terms does the BP ontology have? How many terms does the MF ontology have?
    - The root ID: What is the GO ID of the root term of the BP ontology? What is the GO ID of the root term of the MF ontology?
    - Find the errors such that relationships exist between BP and MF. How many relationships exist between any BP term and any MF term?
    - Find the cases such that two or more different types of relationships exist between two terms. Which pairs of terms have such cases?
    - The number of leaf terms: How many leaf nodes does the BP ontology have? How many leaf nodes does the MF ontology have?
    - The term depth distribution: Suppose the term depth is defined as the shortest path length from the root to the term. Show the histogram of term depth distribution of the BP and MF ontologies, respectively (in Excel).

    """
    input_filename = "go.obo"
    start_time = datetime.now()
    
    ontology_MF,ontology_BP = getDataFromFile(input_filename)
    
    #print(ontology_MF)
    print("length of MF :",len(ontology_MF))
    print("length of BP :",len(ontology_BP))

    for v1 in ontology_MF:
        if ontology_MF[v1] == []:
            root_MF = v1
            print("root node in MF : ",v1)
    for v2 in ontology_BP:
        if ontology_BP[v2] == []:
            root_BP = v2
            print("root node in BP : ",v2)

    error_count = 0
    for id_bp in ontology_BP:
        #print(ontology_BP[id_bp])
        if id_bp == root_BP:
            continue
        for u1 in ontology_BP[id_bp][:]:
            #print(u)
            if u1 in ontology_MF:
                error_count +=1
                ontology_BP[id_bp].remove(u1)
                # print(id_bp,"에서 ",u1,"를 삭제하였습니다.")
                # print(ontology_BP[id_bp])
                #print(type(ontology_BP[v]))
                #print("ERROR! Relation ",u,"and ", v ," : ", u,"is in MF,", v, "is in BP")

    for id_mf in ontology_MF:
        #print(ontology_MF[id_mf])
        if id_mf == root_MF:
            continue
        for u2 in ontology_MF[id_mf][:]:
            if u2 in ontology_BP:
                error_count +=1
                ontology_MF[id_mf].remove(u2)
                
                #print(id_mf,"에서 ",u2,"를 삭제하였습니다.")
                #print(ontology_MF[id_mf])

                #print(type(ontology_MF[v]))
                #print("ERROR! Relation ",u,"and ", v ," : ", u,"is in BP,", v, "is in MF")
    print("error count : ",error_count)

    
    #* leaf node - child node가 없으면 된다. 누군가의 is-a/part-of. => 자식이 있음.
    leaf_count = 0
    
    for v1 in ontology_MF:
        flag = True
        for v2 in ontology_MF:
            if v1 == v2:
                continue
            if v1 in ontology_MF[v2]:
                flag = False
                break
        if flag:
            #print(v1,"is leaf node")
            leaf_count += 1
    print("MF leaf count : ",leaf_count)

    leaf_count = 0
    
    for v1 in ontology_BP:
        flag = True
        for v2 in ontology_BP:
            if v1 == v2:
                continue
            if v1 in ontology_BP[v2]:
                flag = False
                break
        if flag:
            #print(v1,"is leaf node")
            leaf_count += 1
    print("BP leaf count : ",leaf_count)    
    

    #* term depth
    #id: GO:0000006
    # GO:0000006 - GO:0005385 - GO:0046915 - GO:0046873 - GO:0022890 - GO:0008324 - GO:0015075 - GO:0022857 - GO:0005215 - GO:0003674(root)
    #                                                                - GO:0015318 
    # start_node = 'GO:0000064'
    # shortest = getTermDepth(ontology_MF,start_node,root_MF)
    # print(start_node," to root :",shortest)
    filename = 'output_MF.txt'
    path_MF = [0 for i in range(20)]
    path_BP = [0 for i in range(20)]

    for start_node in ontology_MF:
        #print(start_node)
        if start_node == root_MF:
            continue
        shortest = getTermDepth(ontology_MF,start_node,root_MF)
        path_MF[shortest] += 1        
        #print(start_node," to root :",shortest)
        #output_to_file(filename,start_node,shortest)
    #GO:0001098 - GO:0005515 - GO:0005488 - GO:0003674 (root)
    print("path_MF",path_MF[1:])

    filename = 'output_BP.txt'
    for start_node in ontology_BP:
        #print(start_node)
        if start_node == root_BP:
            continue
        shortest = getTermDepth(ontology_BP,start_node,root_BP)
        path_BP[shortest] += 1
        #print(start_node," to root :",shortest)
        #output_to_file(filename,start_node,shortest)
    print("path_BP",path_BP[1:])

    # for v in ontology_MF:
    #     print(v, ontology_MF[v])
    
    
    print("[+] Time Elapsed : ", datetime.now() - start_time, "microseconds")

if __name__ == '__main__':
    main()