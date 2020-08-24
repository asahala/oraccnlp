#!/usr/bin/python
# -*- coding: utf-8 -*-

# BabyFST Auto-Transcriber Lite Heuristic/Statistical model
#
#    To use, type transliteration into ´INPUT_TEXT´ and run.
#    Not compatible with windows commandline due to unicode.
#
#    The default input should give the following probabilities.
#
#    id-di-iš-šu
#    [(1.0, 'iddiššū')]
#
#    E₂
#    [(0.6227381358825538, 'bīt'), (0.29327415500170706, 'bīti'),
#    (0.045749402526459544, 'bītu')]
#    ip-ru-us
#    [(1.0, 'iprus')]
#
#    id-da-ak
#    [(0.8571428571428571, 'iddak'), (0.14285714285714285, 'iddâk')]
#
#    The model learns character to character mappings from the training
#    data and converts them into abstract patterns that can be'
#    generalized to transcribe other similar words. If it cannot
#    produce generalizations (logograms or complex syllabic spellings)
#    it will rely on dictionary lookup.
#
#    Achieves a maximum recall of 92% for syllabic spellings and
#    about 61% for logograms on Standard Babylonian.
#
#    -- github/asahala



import re
import gzip
import itertools
from collections import Counter

INPUT_TEXT = 'id-di-iš-šu E₂ ip-ru-us id-da-ak'

C = 'bdghjklmnpqrsšṣtṭwz'
#C = C + C.upper()
GX = ['-'.join(cc) for cc in zip(C, C)]
GS = [''.join(cc) for cc in zip(C, C)]
replacer = str.maketrans(C, 'C'*len(C))

INDEX = '₀₁₂₃₄₅₆₇₈₉ₓ'
indices = tuple(INDEX)
index_remover = str.maketrans(INDEX, ' '*len(INDEX))

xlitmaps = {}
xlitmaps2 = {}
xlit_affs = []
script_affs = []

def readfile(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        return f.read().splitlines()

def clean(mapping):
    """ Clean OpenNMT data """
    return [x.replace(' ', '').replace('##', '') for x in mapping]

def makepairs(source, target):
    """ Map transliteration to transcription """
    xlit = clean(readfile(source))
    xscript = clean(readfile(target))
    return zip(xlit, xscript)
    
def _remove_indices(string):
    """ Get rid of indices to simplify syllabic transliteration """
    return string.translate(index_remover).replace(' ', '')

def _make_abstraction(string, geminates):
    #string = re.sub('\{.+?\}', '', string)
    for g in geminates:
        string = string.replace(g, '₲')
    return ''.join([c.translate(replacer) for c in string])

def make_affixmaps():
    """ Incorporate typical verb affixes to abstractions to increase
    coverage """
    with open('affix-mappings.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            if line:
                line = line.replace('0', '')
                if not line.startswith('//'):
                    script, xlit = line.split('\t')
                    script_affs.append(script)
                    xlit_affs.append(xlit)

def make_maps(pairs):
    """ Build abstract representations of transliteration
    and transcription """
    a = 0
    b = 0
    for xlit, script in pairs:   
        abs_xlit = _make_abstraction(_remove_indices(xlit), GX)
        abs_script = _make_abstraction(script, GS)
        A = abs_xlit.count('C') + abs_xlit.count('₲')
        B = abs_script.count('C') + abs_script.count('₲')
        xlitmaps2.setdefault(xlit, []).append(script)
        if A == B:
            a += 1
            xlitmaps.setdefault(abs_xlit, []).append(abs_script)
        else:
            b += 1
            #if not re.match('.*[A-Z\{0-9Š].*', xlit): print(xlit, script)
            #xlitmaps.setdefault(xlit, []).append(script)
    print('abstract: %i, exact: %i' % (a, b))
    
def transcribe(xlit, geminates, limit=3):
    """ Transcribe given string; change limit to display fewer
    top results """
    c_table = []
    xlit_ = xlit
    abs_xlit = _make_abstraction(_remove_indices(xlit), GX)
    xlit = _remove_indices(xlit)
    for g in geminates:
        xlit = xlit.replace(g, g[0])

    if xlit_ in xlitmaps2.keys():
        counts = Counter(xlitmaps2.get(xlit_, '---'))
        probs = []
        for k, v in counts.items():
            probs.append(
                (v/sum(counts.values()), k))
        return sorted(probs, reverse=True)[:limit]
    
    elif abs_xlit in xlitmaps.keys():
        for i, c in enumerate(abs_xlit):
            if c in ('₲', 'C'):
                c_table.append(xlit[i])

        options = []
        for abs_script in xlitmaps.get(abs_xlit, ['---']):
            script = ''
            cindex = 0
            for c in abs_script:
                if c in ('₲'):
                    script += c_table[cindex]*2
                    cindex += 1
                elif c in ('C'):
                    script += c_table[cindex]
                    cindex += 1
                else:
                    script += c
            options.append(script)

        counts = Counter(options)
        probs = []
        for k, v in counts.items():
            probs.append(
                (v/sum(counts.values()), k))
        return sorted(probs, reverse=True)[:limit]
    else:
        pass


""" Make training data: Affix mapper and logograms are disabled.
For transcribing logograms one should use the neural model as
it takes the context into account """

training_pairs = makepairs('./transcription_data/oracc-train-src.gz',
                  './transcription_data/oracc-train-tgt.gz')

make_maps(training_pairs)

""" Feed input into transcriber """
for x in INPUT_TEXT.split(' '):
    print(x)
    if 'x' not in x:
        j = transcribe(x, GX, limit=3)
        print(j)
        print('\n')
