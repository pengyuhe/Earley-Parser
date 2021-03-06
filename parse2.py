import os,sys
import math
import heapq
from heapq import heappush,heappop, heapify
from copy import deepcopy,copy


def Attach(Current_Column,S):
    #print("Now attaching")
    h=[]

    heapify(h)
    for Entry in Parse_Chart[Current_Column]:
        ### If the dot has reached the end

        if(Entry == None):
            continue


        ### We build a heap for attaching
        ### Always attach the entry with the smallest weight first
        ### If the new (generated by attach) entry can be attached (has an empty [Term])
        ### Add it to the heap

        if( len ( Entry[2] ) ==0 ): ### This entry can be an attaching candidate
            heappush(h,( Entry[3][0],Entry ) )


    #print("Oringinal heap constructed")


    while(h):
        #print(len(h))
        ### Temp Entry is in current line
        Temp_PEntry=heappop(h)
        Temp_Entry=Temp_PEntry[1]
        #print(Temp_Entry)
        Start_line=Temp_Entry[0]
        Temp_Key=Temp_Entry[1]
        Temp_Weight = Temp_Entry[3][0]



        if(Temp_Key=='ROOT'):
            continue
        ### Maybe can be improved???
        #print("Start_line=",Start_line)
        #print("Current_Column=",Current_Column)


        if (Start_line==Current_Column):
            Attach_List=Parse_Chart[Start_line]
        else:
            Attach_List=Rule_Hash[(Start_line,Temp_Key)]
            #Attach_List=Parse_Chart[Start_line]


        for Attach_Entry in Attach_List:

            ### If it can be attached
            if(Attach_Entry==None):
                continue
            if( len(Attach_Entry[2])==0):
                continue

            if(Attach_Entry[2][0]!=Temp_Key):
                print("OH")
            if(Attach_Entry[2][0]==Temp_Key):
                ### We construct the Attach_Entry
                ### And determine whether we would like to add it
                New_Attach_Entry=deepcopy(Attach_Entry)

                New_Attach_Entry[2].pop(0)
                New_Attach_Entry[3][0]+=Temp_Weight
                
                ### As for the pointer we always do:
                ### The left branch has a non-empty [Terms]
                ### The right branch is either a terminal or has a empty [Terms]
                New_Attach_Entry[3][1][0]=Attach_Entry
                New_Attach_Entry[3][1][1]=Temp_Entry
                ### Check if this new entry is added to Parse_Chart
                Added=0
                '''
                if( Current_Column != len(S) ):
                    word=S[Current_Column]
                    if( len(New_Attach_Entry[2])!=0):
                        if(New_Attach_Entry[2][0] not in Ancestors[word]):
                            continue
                '''
                
                ### Check whether it new entry has been in the current column
                Temp_Hash_value=Hash.get( (Current_Column,(New_Attach_Entry[0],New_Attach_Entry[1],tuple(New_Attach_Entry[2]) ) ), None)
                

                if(Temp_Hash_value==None):   
                    Parse_Chart[Current_Column].append(New_Attach_Entry)

                    Hash[(Current_Column,(New_Attach_Entry[0],New_Attach_Entry[1],tuple(New_Attach_Entry[2]) ) )]=len(Parse_Chart[Current_Column])-1
                    Added=1
                else:
                    Old_Entry=Parse_Chart[Current_Column][Temp_Hash_value]
                    if(Old_Entry[3][0]>New_Attach_Entry[3][0]):
                        Parse_Chart[Current_Column][Temp_Hash_value]=None
                        Parse_Chart[Current_Column].append(New_Attach_Entry)
                        Hash[(Current_Column,(New_Attach_Entry[0],New_Attach_Entry[1],tuple(New_Attach_Entry[2]) ) )]=len(Parse_Chart[Current_Column])-1
                        Added=1
                if(Added==1):
                    if (len(New_Attach_Entry[2])==0):
                        Temp_Entry_local=New_Attach_Entry
                        heappush(h,(Temp_Entry_local[3][0],Temp_Entry_local))
    


def Predict(Current_Column):

    #print("Now predicting")
    ### We use a pointer to go down the chart
    ### Because the first terms are generated by attach
    ### So we can easily start from the head


    ### Optimization for parse2
    ### Because we always predict every possible terms for a key in a batch
    ### and check them each with hash table
    ### Now for each key, after the first batch, we no longer predict it.

    Predict_Check={}


    Current_Predict=0

    while( Current_Predict < len ( Parse_Chart [ Current_Column ] ) ):
        Predict_Entry=deepcopy(Parse_Chart[Current_Column][Current_Predict])
        
        if(Predict_Entry==None or len(Predict_Entry[2])==0 ):
            Current_Predict+=1
        
            continue


        if(Predict_Entry[2][0] in Grammar_Dic):
            Current_Key=Predict_Entry[2][0]
            
            if Current_Key in Predict_Check:
                Current_Predict+=1
                continue
             
            Predict_Check[Current_Key]=1

            ### Optimization: left corner
            ### When we predict do no loop over all the possible rules in the Dic
            ### Instead, we only loop over the reasonable table we just build

            Looplist=[]
            if (Current_Column,Current_Key) in Hash_S:
                for B in Hash_S[(Current_Column,Current_Key)]:
                    Looplist+=RAB[(Current_Key,B)]

            #Hash_S[(Current_Column,Current_Key)]=[]
            
            # print("L looplist is",len(Looplist))

            #print("L Grammar[key] is",len(Grammar_Dic[Current_Key]))

            #for Term in Looplist:
            for Term in Grammar_Dic[Current_Key]:
                ### We construct the entry, and determine whether it should be added
                ### We do not need back pointer for Predict
                New_Entry=[Current_Column,Current_Key,Term[1],[Term[0],[None,None]]]
                
                Hash_Key=(Current_Column, ( Current_Column,Current_Key,tuple(Term[1])  ) )

                if(Hash_Key not in Hash):
                    Parse_Chart[Current_Column].append(New_Entry)
                    Hash[Hash_Key]=len(Parse_Chart[Current_Column])-1
                else:
                    Temp_Hash_value=Hash[Hash_Key]
                    Old_Entry=deepcopy(Parse_Chart[Current_Column][Temp_Hash_value])

                    if(Old_Entry[3][0]>New_Entry[3][0]):
                        Parse_Chart[Current_Column][Temp_Hash_value]=None
                        Parse_Chart[Current_Column].append(New_Entry)
                        Hash[Hash_Key]=len(Parse_Chart[Current_Column])-1
            
        
        Current_Predict+=1
                

### Predict: only deal with the non-terminals
### Scan: only deal with the terminals 
### So they will not bother each other

def Scan(Current_Column,S):

    Success=False

    #print("Now scanning")
    #print("Temp word is",S[Current_Column])
    LC= len(Parse_Chart[Current_Column])

    for i in range(LC-1,-1,-1):
        Temp_Entry=deepcopy(Parse_Chart[Current_Column][i])

        ### Skip all the Non-terminals
        if(Temp_Entry==None):
            continue
        if(len(Temp_Entry[2])==0):
            continue

        if(Temp_Entry[2][0] in Grammar_Dic):
            continue
       

        if(Temp_Entry[2][0]==S[Current_Column]):
            Success=True
            
            ### We construct the new Entry 
            New_Entry=deepcopy(Temp_Entry)
            New_Entry[2].pop(0)
            ### As for the pointer we always do:
            ### The left branch has a non-empty [Terms]
            ### The right branch is either a terminal or has a empty [Terms]
            New_Entry[3][1][0] = Parse_Chart[Current_Column][i]
            New_Entry[3][1][1] = S[Current_Column]

            if len(Parse_Chart)<Current_Column+2:
                Parse_Chart.append([])

            Parse_Chart[Current_Column+1].append(New_Entry)

    return Success


        
def Build_Rule_Hash(Current_Column):
    for Entry in Parse_Chart[Current_Column]:
        #print(Entry)
        if(Entry==None):
            continue
        if( len ( Entry[2] ) ==0 ):
            continue
        Temp_Key=(Current_Column,Entry[2][0])

        if(Temp_Key in Rule_Hash):
            Rule_Hash[Temp_Key].append(Entry)

        else:
            Rule_Hash[Temp_Key]=[Entry]

def Build_SjA(i,Y):
    if(Y not in PB):
        return
    #if(Y in Processed):
    #    return
    #Processed[Y]=1

    for X in PB[Y]:
        if (i,X) not in Hash_S:
            Hash_S[ (i,X) ] = set( [] )
            Hash_S[ (i,X) ].add(Y)
            Build_SjA(i,X)
        else:
            Hash_S[ (i,X) ].add(Y)



def Parse(S):
    LS=len(S) 
    #### Check whether the sentence is a single empty symbol
    if(LS==1):
        if(len(S[0])==0):
            return [None,None]

    if(len(Grammar_Dic)==0):
        return [None,None]
    Parse_Chart.append( [] )

    
    ### Initialize
    ### ROOT may have several rules
    ### Put them all into the chart
    for Element in Grammar_Dic["ROOT"]: 
        Entry=[0,'ROOT',Element[1],[Element[0],[None,None]   ]]
        Parse_Chart[0].append(Entry)

    ### No "ROOT" rule will be added ever again.
    ### No need for putting them into the Hash table
   
    for i in range(0,LS+1):

        ### Optimization: left corner, construct the Hash_S table
        if(i!=LS):### when i==LS, there is no next word
            wordi=S[i]

            ### This function add (j,A) terms to Hash_S table
            Processed={}
            Build_SjA(i,wordi) 
    
        #print("Hash_S=")
        #print(Hash_S)
        #input()


        #for key in Hash_S:
        #    print( key,Hash_S[key] )
        ### We check each step
        Attach(i,S)
        
        Predict(i)
        
        #Print_Chart(i) 
        #input("Press")
        if(i!=LS):
            Build_Rule_Hash(i)


        if(i!=LS):
           Success = Scan(i,S)
           if(Success==False):
               return [None,None]
         
        #input("Press")
        
    '''
    for i in range(0,LS+1):
        Attach(i)
        Predict(i)
        Scan(i,S)
    '''

    ResultValue=None
    Result=None
    for item in Parse_Chart[LS]:
        if(item==None):
            continue
        if item[1]=='ROOT':
            if (Result==None or ResultValue==None or ResultValue>item[3][0]):
                ResultValue = item[3][0]
                Result=item
    return [Result,ResultValue]

def Print_Chart(i):

    
    print("======Parse Chart======")
    for item in Parse_Chart[i]:
        Pitem=deepcopy(item)
        if(Pitem==None):
            print(None)
            continue
        if( isinstance(Pitem[3][1][0],str) ):
            Temp_key1=Pitem[3][1][0]
        elif(Pitem[3][1][0]==None):
            Temp_key1=None
        else:
            Temp_key1=Pitem[3][1][0][1]


        if( isinstance(Pitem[3][1][1],str) ):
            Temp_key2=Pitem[3][1][1]
        elif(Pitem[3][1][0]==None):
            Temp_key2=None
        else:
            Temp_key2=Pitem[3][1][1][1]

        Pitem=[Pitem[0],Pitem[1],Pitem[2],(Pitem[3][0],Temp_key1,Temp_key2)]
        print(Pitem)
    print("====Parse Chart End=======")



def BuildTree(Node,Ancestor):
    #print("Ancestor=",Ancestor)
  
    ### Current Node is a terminal
    if( isinstance(Node,str) ):
        Ancestor.append(Node)
        return
    
    ### Current Node is a good non-terminal
    Flag=0
    if(len(Node[2])==0):
        New_Pointer=[Node[1]]
        if(Ancestor==None):
            Ancestor=deepcopy(New_Pointer)
        else:
            Ancestor.append(New_Pointer)
            Flag=1

    try:
        AA=Node[3][1][0]
    except IndexError:
        print("Node=",Node,"Node Len=",len(Node),"Type is",type(Node))
    if(Node[3][1][0]!=None):
        if(Flag):
            BuildTree(Node[3][1][0],New_Pointer)
        else:
            BuildTree(Node[3][1][0],Ancestor)

    if(Node[3][1][1]!=None):
        if(Flag):
            BuildTree(Node[3][1][1],New_Pointer)
        else:
            BuildTree(Node[3][1][1],Ancestor)
    
    return Ancestor

def Print_Grammar():

    for item in Grammar_Dic:
        print(item)


def Prune_Read_Grammar(NonTerminals,S):

    ### All the keys in Grammar is Non_terminals
    ### If we get rid of all the possible terminals of one non_terminal
    ### Then this non_terminal will not in the dic
    ### In other words, this non_terminal is no longer legal
    ### but there may be some other rules that generate this non_terminal
    ### so those rules are also no longer valid
    ### so we need to prune the grammar recursively
    ### until the num of keys no longer change.

    L_NT_Primary=len(NonTerminals)
    Terminals=set(S)


    Legal_Symbols=NonTerminals.union(Terminals)
    #print("Legal_Symbols are",Legal_Symbols)


    ### Grammar_Temp is the grammar generated by last iteration
    ### initially it equals to the original grammar
    global Grammar_Temp
    global Grammar_Dic

    for Key in Grammar_Temp:
        Temp_Grammar=[]
        Terms=Grammar_Temp[Key]
        for term in Terms:
            Symbols =term[1]
            illegal=0
            for symbol in Symbols:
                if(symbol not in Legal_Symbols):
                    illegal=1
                    break
            if illegal==0:
                Temp_Grammar.append(term)

        if(len(Temp_Grammar)!=0):
            Grammar_Dic[Key]=Temp_Grammar
    
    New_NonTerminals=set( Grammar_Dic.keys() )
    L_NT_New=len(New_NonTerminals)

    ### We keep pruning it iteratively to get rid of all unnecessary rules.
    if(L_NT_New!=L_NT_Primary):
        #print("L_NT_Primary== ",L_NT_Primary)
        #print("L_NT_New== ",L_NT_New)
        Grammar_Temp=deepcopy(Grammar_Dic)
        Grammar_Dic={}
        Prune_Read_Grammar(New_NonTerminals,S)
    else:
        return 

def List_to_tuple(A):
    LA=len(A)
    for i in range(0,LA):
        if type(A[i])==list:
            A[i]=List_to_tuple(A[i])

    return tuple(A)


def Tprint(Tree):
    # This function deals with how to properly print the tree structure generate by Generate_Tree
    L=len(Tree)

    # The form of Tree is a recursive list
    # List[ element, List[ element,element, List[....]]]

    # In the beginning of a list, print '('
    print '(',
    for i in range(0,L):
        if(type(Tree[i]) is list):
            # Recursively 
            Tprint(Tree[i])
        else:
            print Tree[i]," ",
        if(i==L-1):
            # In the end, print ')'
            print ')',

def Build_R_P():
    for key in Grammar_Dic:
        for term in Grammar_Dic[key]:
            Temp_A=copy(key)
            Temp_B=copy(term[1][0])
            #print("TempA=",Temp_A)
            #print("TempB=",Temp_B)
            if( (Temp_A,Temp_B) not in RAB):
                if(Temp_B not in PB):

                    PB[Temp_B]=set([Temp_A])
                    
                else:
                    PB[Temp_B].add(Temp_A)

                RAB[ (Temp_A,Temp_B) ]=[] 
                RAB_Term=deepcopy(term)
                RAB[ (Temp_A,Temp_B) ].append(RAB_Term)
            else:

                RAB_Term=deepcopy(term)
                RAB[ (Temp_A,Temp_B) ].append(RAB_Term)

def Build_Ancestors(Symbol,Now_Stack):


    if(Symbol not in Grammar_Dic):
        Ancestors[Symbol] = set(Now_Stack)
        return
    else:
        if Symbol in Now_Stack:
            return
        else:
            Stack=deepcopy(Now_Stack)
            Stack.append(Symbol)
            for term in Grammar_Dic[Symbol]:
                for symbol in term[1]:
                    Build_Ancestors(symbol,Stack)

if __name__=='__main__':
    try:
        Grammar_file=sys.argv[1]
        Sentence_file=sys.argv[2]
    except ValueError:

        print( "illegal input")
        exit(0)
    
    with open(Grammar_file) as f:
        Grammar_content=f.readlines()

    
    ### We make theses things global:
    ### Parse Chart, Hash table, 
    global Grammar_Dic
    global Parse_Chart
    global Hash
    global Grammar_Copy
    global Grammar_Temp
    global Left_Corner_Table
    global Rule_Hash
    global Ancestors
    
    global RAB
    global PB
    global Hash_S
    global Processed


    RAB={}
    PB={}
    Hash_S={}
    Grammar_Dic={}
    Parse_Chart=[]
    Hash={}
    Processed={}

    ### Read grammar
    for Temp_grammar in Grammar_content:
        Temp_grammar=Temp_grammar.strip('\n')
        LS_grammar=Temp_grammar.split('\t')
        #print(LS_grammar)
        Weight=-math.log(float(LS_grammar[0]) )/math.log(2)
        Key=LS_grammar[1]
        Term=LS_grammar[2].split(' ')
        if(Grammar_Dic.get(Key,None)==None):
            Grammar_Dic[Key]=[ (Weight,Term) ]
        else:
            Grammar_Dic[Key].append( (Weight,Term) )



    NonTerminals=set(Grammar_Dic.keys())
    
    Grammar_Copy=deepcopy(Grammar_Dic)
    Grammar_Temp=deepcopy(Grammar_Dic)


    with open(Sentence_file) as f:
        Sentences=f.readlines()
    
    Tree=[]
    for S in Sentences:
        S=S.strip('\n')
        S=S.split(' ')
        Parse_Chart=[]
        Hash={}
        print "S=",S

        ### Optimization: Pruning the grammar to delete all the non-terminals which are not in the current sentences
        Grammar_Dic={}
        Grammar_Temp=deepcopy(Grammar_Copy)
        ### Generate new and smaller Grammar_Dic by this pruning equation
        Prune_Read_Grammar(NonTerminals,S)

        Rule_Hash={}

        ### Optimization: left corner
        RAB={}
        PB={}
        Hash_S={}
        Processed={}

        Ancestors={}
        ### This function construct the RAB and PB based on current grammar
        Build_R_P()
            

        ### This function construct all the ancestor

        #Build_Ancestors('ROOT',[])


        #print(Ancestors)


        #input()
        #print("RAB=")
        #print(RAB)
        #print("PB=")
        #print(PB)

        #input("s")

        #Print_Grammar()
        Tree=Parse(S)
        ### Tree[0] is the raw tree
        ### Tree[1] is the best weight
        if(Tree[0]!=None):
            PrintTree=BuildTree(Tree[0],None)
            Tprint(PrintTree)
            print("Best Weight = ",Tree[1])
        else:
            print(None)
        
        #Temp_Pause=input("Anything")


