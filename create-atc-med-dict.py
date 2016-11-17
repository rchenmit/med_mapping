import argparse
import json
import queryRxNorm as qrx
import formatMed as fm

# time release technology
# source: https://en.wikipedia.org/wiki/Time_release_technology
rt = set(['cd', 'cr', 'dr', 'er', 'ir', 'la', 'mr', 'sa', 'sr',
          'tr', 'xl', 'xr', 'xt', 'generic'])


def check_rtech(drug):
    drugWords = drug.lower().split()
    cleanWords = set(drugWords).difference(rt)
    cleanWords = sorted(cleanWords, key=drugWords.index)
    return ' '.join(cleanWords)


def get_atc(drug):
    # try first to look up rxcui since it does name match
    _, rxcui = fm.lookup_rxcui(drug)
    atcClass = None
    if rxcui is None:
        # split and try the last one
        drugWords = drug.split()
        if len(drugWords) > 1:
            for idx in [-1, 0]:
                drugPrime = drugWords[idx]
                _, rxcui = fm.lookup_rxcui(drugPrime)
                if rxcui is not None:
                    continue
    if rxcui is not None:
        atcClass = qrx.rxcui_to_category(rxcui, relaSource="ATC")
    if atcClass is None or len(atcClass) == 0:
        return qrx.drug_to_category(drug, "ATC")
    return atcClass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="input filename")
    parser.add_argument("outfile", help="output filename")
    args = parser.parse_args()
    medCount = json.load(open(args.infile, 'rb'))
    atcDict = {}
    # sort based on highest count and reverse back
    for k, v in sorted(medCount.iteritems(), key=lambda (k, v): (v, k),
                       reverse=True):
        if k == "":
            continue
        # fix the synonyms
        k, _, _ = fm.fix_synonyms(k, k.split(), {})
        atcClass = get_atc(k)
        if atcClass is not None and len(atcClass) > 0:
            print k, "->", atcClass
            atcDict[k] = atcClass
        else:
            print "Unable to resolve:", k
    with open(args.outfile, "w") as outfile:
        json.dump(atcDict, outfile,)

if __name__ == "__main__":
    main()
