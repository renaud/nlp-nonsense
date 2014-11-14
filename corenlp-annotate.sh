
HERE=`dirname $0`
INFILE=${1:-"$HERE/data/test.txt"}
OUTDIR=${2:-`dirname $INFILE`}
ANNOTATORS="tokenize,ssplit,pos,lemma,ner"
java -cp "$HERE/corenlp/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP \
	-annotators $ANNOTATORS \
	-file $INFILE -outputDirectory $OUTDIR

