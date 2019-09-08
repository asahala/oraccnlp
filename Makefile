SHELL=/bin/bash

TRAINPARSER=${TURKU_PARSER}/train/train_models.py
TRAINONMT=${OPENNMT}/train.py
EMBEDDING=models/akk.vectors
CURRDIR=$(shell pwd)

SETTINGS=transcr transl
DATA=${SETTINGS:%=data/oracc-%-train.conllu} \
     ${SETTINGS:%=data/oracc-%-dev.conllu} \
     ${SETTINGS:%=data/oracc-%-test.conllu}
PARSERS=${SETTINGS:%=models/oracc-%-parser} 

all:${DATA} 
	echo ${DATA}

${DATA}:resources/ORACC.VRT
	python3 src/oracc2conllu.py $^ data/oracc

models/oracc-%-parser:data/oracc-%-train.conllu data/oracc-%-dev.conllu 
	# The only way to run the Turku parser afaik is to run it in
	# the directory ${TURKU_PARSER}. Therefore, the following
	# hackish solution.
	cd ${TURKU_PARSER}; \
	source venv-parser-neural/bin/activate; \
	python3 train/train_models.py --force_delete \
	                              --name oracc-$*-parser \
                                      --train_file ${CURRDIR}/data/oracc-$*-train.conllu \
		                      --devel_file ${CURRDIR}/data/oracc-$*-dev.conllu \
                                      --embeddings ${CURRDIR}/${EMBEDDING}
	rm -Rf models/oracc-$*-parser
	mv ${TURKU_PARSER}/models_oracc-$*-parser models/oracc-$*-parser

results/oracc-%-test.conllu.sys:data/oracc-%-test.conllu models/oracc-%-parser
	# See the training target for documentation.
	cd ${TURKU_PARSER}; \
	source venv-parser-neural/bin/activate; \
	cat ${CURRDIR}/$< | bash ${CURRDIR}/src/clear_annotations.sh |\
	python3 ${TURKU_PARSER}/full_pipeline_stream.py \
                --conf ${CURRDIR}/models/oracc-$*-parser/pipelines.yaml \
                parse_conllu > ${CURRDIR}/$@

