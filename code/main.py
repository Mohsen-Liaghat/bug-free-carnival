from queue import Queue
from random import choices
from math import exp
import pandas as pd 
from itertools import chain, combinations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class ENV : 
    def __setdefaultq( self , i , j , uf , dest ) :
        if uf not in self.__q :
            self.__q[uf] = dict()
        if i not in self.__q[uf] :
            self.__q[uf][i] = dict()
        if j not in self.__q[uf][i] :
            self.__q[uf][i][j] = dict()
        if dest in self.__q[uf][i][j] :
            return False
        
        self.__q[uf][i][j][dest] = 0
        return True
    
    def q2latex( self ) :
        tmp = open("tmp.tex" , "w")
        tmp.write("\\begin{longtable}{|c|c|c|c|c|}\n state & N & S & E & W \\\\\n \\hline\n\\hline\n")
        for i in self.__q :
            subflag = self.__q[i] 
            for j in subflag :
                subflagr = subflag[j] 
                for k in subflagr :
                    subflagrc = subflagr[k]
                    tmp.write(str(i) + "," + str(j) + "," + str(k) )
                    m = max( subflagrc.values() )
                    for d in "NSEW" :
                        if d in subflagrc :
                            if subflagrc[d] == m :
                                tmp.write("& \\textcolor{blue}{" + "{:.3}".format(float(subflagrc[d])) + "}")
                                m += 1
                            else :
                                tmp.write("&" + "{:.3}".format(float(subflagrc[d])) )
                        else :
                            tmp.write("&")
                    tmp.write("\\\\\n\\hline\n")
        tmp.write("\\end{longtable}")
        tmp.close()


    #preparing q table
    def __pq ( self , m ) :
        self.__q = dict()
        traceq = Queue()
        traceq.put( ( self.__start[0] , self.__start[1] , self.__flags ) )
        
        while not traceq.empty() :
            tmp = traceq.get()
            i = tmp[0]
            j = tmp[1]
            uf = tmp[2]
            if i != len(m) - 1 : 
                if ( i + 1 , j ) in uf :
                    if self.__setdefaultq(i, j, tuple(uf), 'S') : 
                        tmp = uf.copy() 
                        tmp.remove((i + 1 , j))
                        traceq.put( ( i + 1 , j , tmp ) )
                elif m[i + 1][j] != 'B' :
                    if self.__setdefaultq(i, j, tuple(uf), 'S') :
                        traceq.put( (i + 1 , j , uf) )
            if i != 0 :
                if ( i - 1 , j ) in uf :
                    if self.__setdefaultq(i, j, tuple(uf), 'N') : 
                        tmp = uf.copy()
                        tmp.remove( ( i - 1 , j ) )
                        traceq.put( ( i - 1 , j , tmp ) )
                elif m[i - 1][j] != 'B' :
                    if self.__setdefaultq(i, j, tuple(uf), 'N') :
                        traceq.put( (i - 1 , j , uf) )
            if j != len(m[i]) - 1 : 
                if ( i , j + 1 ) in uf :
                    if self.__setdefaultq(i, j, tuple(uf), 'E') : 
                        tmp = uf.copy()
                        tmp.remove( ( i , j + 1 ) )
                        traceq.put( (i , j + 1 , tmp ) )
                elif m[i][j+1] != 'B' :
                    if self.__setdefaultq(i, j, tuple(uf), 'E') :
                        traceq.put( (i , j + 1 , uf) )
            if j != 0 :
                if ( i , j - 1 ) in uf :
                    if self.__setdefaultq(i, j, tuple(uf), 'W') : 
                        tmp = uf.copy()
                        tmp.remove( ( i , j - 1 ) )
                        traceq.put( (i , j - 1 , tmp ) )
                elif m[i][j-1] != 'B' :
                    if self.__setdefaultq(i, j, tuple(uf), 'W') :
                        traceq.put( (i , j - 1 , uf) )
                
    #     print("the states has been minimized.")
    def __input_error( self , maze ) :
        valid_symbols = {"A" : 0 , "B" : 0 , "W" : 0 , "T" : 0 , "F" : 0}

        # error checking 
        
        for i in range(len(maze)) :
            maze[i].upper() 
            for j in maze[i] :
                if j not in valid_symbols :
                    raise Exception(str(j) + " is not in valid symbols.")
                else : 
                    valid_symbols[j] += 1
        if valid_symbols["A"] != 1 :
            raise Exception("must be a single agent in this map.")
        if valid_symbols["W"] == 0 : 
            raise Exception("there is no way in this map.")
        if valid_symbols["T"] != 1 : 
            raise Exception("must be a single target in this map.")

    def __init__(self , maze ) :
        self.__input_error( maze )

        self.__flags = []
        for i in range(len(maze)) :
            for j in range( len(maze[i] ) ) :
                if maze[i][j] =='W' or maze[i][j] == 'B' : 
                    pass
                elif maze[i][j] == 'F' :
                    self.__flags.append(( i , j ))
                elif maze[i][j] == 'A' :
                    self.__start = ( i , j )
                elif maze[i][j] == 'T' :
                    self.__target = ( i , j )
        self.__agentpos = ( self.__flags , self.__start[0] , self.__start[1] )
        print("environment has been created")

        self.__pq(maze)

    def reset( self ) :
        self.__agentpos = ( self.__flags , self.__start[0] , self.__start[1] )

    def any_unseened_flag ( self ) :
        if self.__agentpos[0] == [] :
            return True 
        return False

    def moov( self , dest , alpha , gamma ) :
        if dest not in self.__q[tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]] :
            raise Exception("invalid destination")
        if dest == 'N' :
            dest2 = ( self.__agentpos[1] - 1 , self.__agentpos[2] )
        elif dest == 'S' :
            dest2 = ( self.__agentpos[1] + 1 , self.__agentpos[2] )
        elif dest == 'E' :
            dest2 = ( self.__agentpos[1] , self.__agentpos[2] + 1 )
        elif dest == 'W' :
            dest2 = ( self.__agentpos[1] , self.__agentpos[2] - 1 )

        r = -1 
        if dest2 == self.__target and not self.any_unseened_flag() :
            r = len(self.__flags) + 1 
        if (dest2[0] , dest2[1]) in self.__agentpos[0] :
            r = 1
            tmp = self.__agentpos[0].copy()
            tmp.remove(dest2)
            dest2 = ( tmp, ) + dest2
        else :
            dest2 = ( self.__agentpos[0], ) + dest2
        #posible future reward
        pfr = [ self.__q[tuple(dest2[0])][dest2[1]][dest2[2]][i] for i in self.__q[tuple(dest2[0])][dest2[1]][dest2[2]] ]

        self.__q[tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]][dest] = ( 1 - alpha ) * self.__q[tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]][dest] + alpha * ( r + gamma * max(pfr) )

        self.__agentpos = dest2

    def episod ( self , alpha , gamma , max_round , round ) :
        path = ""
        while self.__agentpos != ( [], ) + self.__target and len(path) <= 10000 :
            c =  choices( list ( self.__q[tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]].keys() ) , 
                    [ exp( max ( min( self.__q[tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]][i] / ( max_round - round ) , 709 ) , -744 )) for i in self.__q[ tuple(self.__agentpos[0])][self.__agentpos[1]][self.__agentpos[2]] ] , 
                    k = 1 )[0]
            path += c
            self.moov( c , alpha , gamma)

    def fill_qtable( self , tround , alpha , gamma ) :
        for i in range( tround ) :
            print( "round" , i , ":")
            self.episod( alpha, gamma, tround, i )
            self.reset()
        self.q2latex() 
    

def main() :
    print("enter the environment map then enter an empty line")
    maze = []
    row = input()
    while row != "" :
        maze.append(row) 
        row =input()
    
    env = ENV(maze)
    env.fill_qtable( tround= 10000 , alpha= 0.5, gamma= 0.5 )


if __name__ == "__main__" :
    main()
    