#!/usr/bin/env python
#
# takes a treelist of all trees that we want to form pathes among them
#
import sys
import os

import pathtrees.pathtrees as pt
import pathtrees.likelihood as like
import pathtrees.phylip as ph
import pathtrees.tree as tree
import pathtrees.MDS as plo

import numpy as np
import time
#import shutil

GTPTREELIST = 'gtptreelist' # a pair of trees formed from the master treelist
GTPTERMINALLIST = 'terminal_output_gtp'  #GTP terminal output
NUMPATHTREES = 10  #number of trees in path
GTP = 'pathtrees/gtp'

def create_treepair(ti,tj):
    f = open(GTPTREELIST,'w')
    f.write(ti.strip())
    f.write("\n")
    f.write(tj.strip())
    f.write('\n')

def run_gtp(gtptreelist,gtpterminallist):
    os.system(f"cd  {GTP}; java -jar gtp.jar -v ../../{gtptreelist} > ../../{gtpterminallist}")
    
def masterpathtrees(treelist): #this is the master treelist
    # loop over treelist:
    allpathtrees = []
    for i,ti in enumerate(treelist):
        for j,tj in enumerate(treelist):
            if j>=i:
                continue
            #form a treelist of the pair
            create_treepair(ti,tj) #this writes into a file GTPTREELIST
            #print("run gtp")
            run_gtp(GTPTREELIST, GTPTERMINALLIST)
            mypathtrees = pt.pathtrees(GTPTREELIST, GTPTERMINALLIST, NUMPATHTREES)
            #print("LOOP",i,j)
            allpathtrees.extend(mypathtrees)
            #save or manipulate your pathtrees
    return [a.strip() for a in allpathtrees]

def likelihoods(trees,sequences):
    likelihood_values=[]
    for i,newtree in enumerate(trees):
        t = tree.Tree()
        t.myread(newtree,t.root)
        t.insertSequence(t.root,labels,sequences)
        
        #setup mutation model
        # the default for tree is JukesCantor,
        # so these two steps are not really necessary
        Q, basefreqs = like.JukesCantor()
        t.setParameters(Q,basefreqs)
        #calculate likelihood and return it
        t.likelihood()
        likelihood_values.append(t.lnL)
    return likelihood_values

def store_results(outputdir,filename,the_list):
    completename = os. path. join(outputdir, filename)
    np.savetxt (completename, the_list,  fmt='%s')

def myparser():
    import argparse
    parser = argparse.ArgumentParser(description='Create a geodesic path between all trees in the treelist, a treefile and a sequence data file are mandatory, if the the option -r N is used then the treefile (which can be empty) will be augemented with N random trees and the pathtree method is then run on those trees')
    parser.add_argument('STARTTREES', 
                        help='mandatory input file that holds a set of trees in Newick format')
    parser.add_argument('DATAFILE', 
                        help='mandatory input file that holds a sequence data set in PHYLIP format')
    parser.add_argument('-o','--output', dest='outputdir', #action='store_const',
                        #const='outputdir',
                        default='pathtree_outputdir',
                        help='directory that holds the output files')
    parser.add_argument('-v','--verbose', action='store_true',
                        default=None, #const='keep_intermediate',
                        help='Do not remove the intermediate files generated by GPT')
    parser.add_argument('-p','--plot',dest='plotfile',
                        default=None, action='store',
                        help='Create an MDS plot from the generated distances')
    parser.add_argument('-n','--np', '--numpathtrees', dest='NUMPATHTREES',
                        default=10, action='store',type=int,
                        help='Number of trees along the path between two initial trees')
    parser.add_argument('-b','--best', '--numbesttrees', dest='NUMBESTTREES',
                        default=10, action='store',type=int,
                        help='Number of trees selected from the best likliehood trees for the next round of refinement')
    parser.add_argument('-r','--randomtrees', dest='num_random_trees',
                        default=0, action='store',type=int,
                        help='Generate num_random_trees rooted trees using the sequence data individual names.')

    parser.add_argument('-g','--outgroup', dest='outgroup',
                        default=None, action='store',
                        help='Forces an outgroup when generating random trees.')

    parser.add_argument('-i','--iterate', dest='num_iterations',
                        default=0, action='store',type=int,
                        help='Takes the trees, generates the pathtrees, then picks the 10 best trees and reruns pathtrees, this will add an iteration number to the outputdir, and also adds iteration to the plotting.')

    parser.add_argument('-e','--extended', dest='phyliptype',
                        default=None, action='store_true',
                        help='If the phylip dataset is in the extended format, use this.')
    parser.add_argument('-bound','--hull', '--boundary', dest='proptype',
                        default=None, action='store_true',
                        help='Start the iteration using a convex hull instead of n best likelihood trees.')

    args = parser.parse_args()
    return args

    
if __name__ == "__main__":
    DEBUG = False
    args = myparser() # parses the commandline arguments
    start_trees = args.STARTTREES
    datafile = args.DATAFILE
    outputdir = args.outputdir
    keep = args.verbose == True
    num_random_trees = args.num_random_trees
    outgroup = args.outgroup
    num_iterations = args.num_iterations+1
    plotfile = args.plotfile
    proptype = args.proptype
    phyliptype = args.phyliptype
    if phyliptype:
        type = 'EXTENDED'
    else:
        type = 'STANDARD'
    if num_iterations<=1:
        os.system(f'mkdir -p {outputdir}')
        outputdir = [outputdir]
        if plotfile != None:
            plotfile2 = "contour_"+plotfile
    else:
        plotfile2 = []
        o = outputdir
        outputdir=[]
        for it in range(1,num_iterations):
            os.system(f'mkdir -p {o}{it}')
            outputdir.append(f'{o}{it}')
            plotfile2.append(f"contour_{it}_{plotfile}")

    NUMPATHTREES = args.NUMPATHTREES
    NUMBESTTREES = args.NUMBESTTREES

    #    print(args.plotfile)
    print(args)

    labels, sequences, variable_sites = ph.readData(datafile, type)
    #print(labels)
    #print(variable_sites)
    #sys.exit()
    if num_random_trees>0:
        from numpy.random import default_rng
        totaltreelength = ph.guess_totaltreelength(variable_sites)
        rng = default_rng()        
        randomtrees = [tree.generate_random_tree(labels, rng.uniform(0.2,100)*totaltreelength, outgroup) for _ in range(num_random_trees)]
        #print(randomtrees)
        #sys.exit()
        with open(start_trees,'a') as f:
            for rt in randomtrees:
                print(rt,file=f)
    print(f'Calculating paths through tree space')
    tictotal = time.perf_counter()
    with open(start_trees,'r') as f:
        StartTrees = [line.strip() for line in f]
    # iterations, this is done at least once for standard operation
    #
    for it1 in range(1,num_iterations):
        tic = time.perf_counter()
        it = it1-1
        print(f'Iteration {it1}')
        store_results(outputdir[it],f'starttrees-{it1}',StartTrees)
        Pathtrees = masterpathtrees(StartTrees)
        Treelist= StartTrees+Pathtrees
        Likelihoods = likelihoods(Treelist,sequences)
    
        store_results(outputdir[it],'likelihood',Likelihoods)
        store_results(outputdir[it],'treelist',Treelist)
        store_results(outputdir[it],'starttrees',StartTrees)
        store_results(outputdir[it],'pathtrees',Pathtrees)
        toc = time.perf_counter()
        time1 = toc - tic
        print(f"Time of generating pathtrees results = {time1}")
        tic2 = time.perf_counter()
        #if DEBUG:
        newtreelist = os.path.join(outputdir[it], 'treelist')
        print('Calculate geodesic distance among all pathtrees')
        run_gtp(newtreelist, GTPTERMINALLIST)
        os.system(f'mv pathtrees/gtp/output.txt {outputdir[it]}/')
        if not keep:
            os.system(f'rm {GTPTERMINALLIST}')
            os.system(f'rm {GTPTREELIST}')
        toc2 = time.perf_counter()
        time2 = toc2 - tic2
        print(f"Time of GTP distances of all trees = {time2}")
        #if experiment:
        bestlike = plo.bestNstep_likelihoods(Likelihoods,20,2)
        print("@",bestlike)
        #else:
        #    bestlike = plo.best_likelihoods(Likelihoods)
        if plotfile != None:
            n = len(Treelist)
            N= len(Pathtrees)
            distancefile = os.path.join(outputdir[it], 'output.txt')
            distances = plo.read_GTP_distances(n,distancefile)
            if DEBUG:
                plo.plot_MDS(plotfile, N, n, distances, Likelihoods, bestlike, Treelist, Pathtrees)
            plo.interpolate_grid(plotfile2[it], N, n, distances,Likelihoods, bestlike, StartTrees)
        if it1 < num_iterations:
            StartTrees = [Treelist[tr] for tr in list(zip(*bestlike))[0]]
            print("@length of start trees after an iteration: ",len(StartTrees))
