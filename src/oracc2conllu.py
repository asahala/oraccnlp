from sys import argv, stderr
import re
import io
import xml.etree.ElementTree as ET

MORFEATURES='_'
DEPREL='child'

def read_vrt(fn):
    with open(fn) as f:
        xml = f.read()        
        # Replace a large number of literal ampersands with entities.
        xml = re.sub(r"&(?![^\t\n]+;)", r"&amp;",xml)
        corpus = ET.parse(io.StringIO("<root>%s</root>" % xml))
        return [ch.text for ch in corpus.iter() if ch.tag == "sentence"]

def oracc2conllu(tree,output_transl):
   """Construct a fake conllu dependency tree where the first token in
   the sentence is the root and all other tokens are direct dependents
   of the first one.

   """
   lines = [l.split('\t') for l in tree.split('\n') if l != '']
   conllu_tree = []
   # I don't know what half of these fields are, actually...
   for trsl1, trscr1, lem1, glos1, pos1, glos2,\
       pos2, _, lcode, _trsl2, _trscr2, _lem2, _id\
       in lines:
       conllu_tree.append('\t'.join((str(len(conllu_tree) + 1),
                                     trsl1 if output_transl else trscr1,
                                     lem1,
                                     pos1,
                                     pos1,
                                     MORFEATURES,
                                     '0' if conllu_tree == [] else '1',
                                     'root' if conllu_tree == [] else DEPREL,
                                     'root' if conllu_tree == [] else DEPREL,
                                     glos1)))
   return '\n'.join(conllu_tree) + '\n'

if __name__=="__main__":
    if len(argv) != 3:
        print("USAGE: %s VRT_FILE OUTPUT_CONLLU_FILE_PREFIX",
              file=stderr)
        exit(1)
        
    input_vrt_fn = argv[1]
    output_conllu_fn = argv[2]

    trees = read_vrt(input_vrt_fn)
    
    for tree_type in "transcr transl".split(' '):    
        train_of = open("%s-%s-train.conllu" % (output_conllu_fn, tree_type),'w')
        dev_of = open("%s-%s-dev.conllu" % (output_conllu_fn, tree_type),'w')
        test_of = open("%s-%s-test.conllu" % (output_conllu_fn,tree_type),'w')
    
        for i,tree in enumerate(trees):
            conllu_tree = oracc2conllu(tree,tree_type=="transl")
            if i % 10 == 0:
                print(conllu_tree,file=test_of)
            elif i % 10 == 9:
                print(conllu_tree,file=dev_of)
            else:
                print(conllu_tree,file=train_of)
