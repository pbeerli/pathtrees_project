# pathtrees_project
Path trees among pairs of trees


usage: pathtrees.py [-h] [-o OUTPUTDIR] [-v] [-p PLOTFILE] [-n NUMPATHTREES] [-r NUM_RANDOM_TREES]
                    STARTTREES DATAFILE

Create a geodesic path between all trees in the treelist, a treefile and a sequence data file are
mandatory, if the the option -r N is used then the treefile (which can be empty) will be augemented with N
random trees and the pathtree method is then run on those trees

positional arguments:
  STARTTREES            mandatory input file that holds a set of trees in Newick format
  DATAFILE              mandatory input file that holds a sequence data set in PHYLIP format

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTDIR, --output OUTPUTDIR
                        directory that holds the output files
  -v, --verbose         Do not remove the intermediate files generated by GPT
  -p PLOTFILE, --plot PLOTFILE
                        Create an MDS plot from the generated distances
  -n NUMPATHTREES, --np NUMPATHTREES, --numpathtrees NUMPATHTREES
                        Number of trees along the path between two initial trees
  -r NUM_RANDOM_TREES, --randomtrees NUM_RANDOM_TREES
                        Generate num_random_trees rooted trees using the sequence data individual names.
			
