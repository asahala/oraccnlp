## Dependencies

1. Install the [Turku Neural Parser Pipeline](https://turkunlp.org/Turku-neural-parser-pipeline/).
1. Get the [OpenNMT toolkit](https://github.com/OpenNMT/OpenNMT-py) and `pip` install requirements.

Add the following lines to your `~/.bashrc` file and execute `source ~/.bashrc`.

```
export TURKU_PARSER=/path/to/Turku-neural-parser-pipeline
export OPENNMT=/path/to/OpenNMT-py
```

## Required files

You need the [Akkadian word embeddings](https://www.dropbox.com/s/hbtxvibhciybwla/akk.vectors.gz?dl=0). Extract the archive and place `akk.vectors` in the `models` directory.

You need the [ORACC corpus](https://www.dropbox.com/s/txnl21dv8r7iuk2/ORACC.VRT.gz?dl=0). Extract the archive and place `ORACC.VRT` in the `resources` directory.

## Building parsers

You can build two different parsers:

1. `models/oracc-transcr-parser` which takes transcribed word forms as input, and
1. `models/oracc-transl-parser` which instead takes transliterated forms as input.

In order to build the transcr-model, run `make models/oracc-transcr-parser`. The other one is built similarly.

## Running parsers

In order to run the transcr-parser on the dev data, run `make results/oracc-transcr-dev.conllu.sys`. The other parser is run similarly.

## Evaluating parsers

In the `src` directory, you can find the official CoNLL 2018 depedendency parsing shared task evaluation script. It is used in the following way and should output something like this:

```
$ python3 src/conll18_ud_eval.py -v data/oracc-transcr-test.conllu results/oracc-transcr-test.conllu.sys 

Metric     | Precision |    Recall |  F1 Score | AligndAcc
-----------+-----------+-----------+-----------+-----------
Tokens     |    100.00 |    100.00 |    100.00 |
Sentences  |    100.00 |    100.00 |    100.00 |
Words      |    100.00 |    100.00 |    100.00 |
UPOS       |     97.00 |     97.00 |     97.00 |     97.00
XPOS       |      0.00 |      0.00 |      0.00 |      0.00
UFeats     |    100.00 |    100.00 |    100.00 |    100.00
AllTags    |      0.00 |      0.00 |      0.00 |      0.00
Lemmas     |     97.01 |     97.01 |     97.01 |     97.01
UAS        |    100.00 |    100.00 |    100.00 |    100.00
LAS        |    100.00 |    100.00 |    100.00 |    100.00
CLAS       |    100.00 |    100.00 |    100.00 |    100.00
MLAS       |     97.03 |     97.03 |     97.03 |     97.03
BLEX       |     96.50 |     96.50 |     96.50 |     96.50
```


## N-Best lemmatization

TBD
