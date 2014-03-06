from split2k import ksplitGraphFile


counter = 0
fileFullPath = r"D:\User's documents\technion\project\eclipse\WORKSPACE\workset\cloneWars\2nd_experiment_presicion\source\wget_v1_10_source-not-strip\funcgraphs\getftp.gml" 
for g in ksplitGraphFile(3, fileFullPath, True):
    counter +=1
    
print counter