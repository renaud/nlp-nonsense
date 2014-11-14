package edu.stanford.iftenney;

import java.io.*;
import java.util.*;
import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.*;
import edu.stanford.nlp.ling.CoreAnnotations.*;

import org.json.simple.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class Main {

    public static void main(String[] args) throws IOException {
	    System.out.println("Hello World!");
        System.out.println("If you see this, I got the build system to work.");

        JSONParser jp = new JSONParser();
        //String path = "/home/iftenney/afs/nlp-nonsense/data/";
        String path = "data/";
        Object obj = null;
        try {
            EncodingFileReader fileReader = new EncodingFileReader(path + "test.txt.annotated");
            obj = jp.parse(fileReader);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        }
        JSONObject dataset = (JSONObject)obj;

        // Make list of sentences
        List<Annotation> sentences = new ArrayList<>(dataset.size());
        for (Object key : dataset.keySet()) {
            JSONArray ja = (JSONArray)dataset.get((String)key);

            sentences.add(new Annotation((String)ja.get(0)));

            String out = String.format("%s -> %s", ja.get(0), ja.get(1));
            System.out.println(out);
        }
        //System.out.println(dataset.keySet().toString());

        // Set up CoreNLP pipeline to pre-annotate
        Properties props = new Properties();
        props.setProperty("annotators",
                "tokenize, ssplit, pos, lemma, ner");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        // Run pipeline
        long startTime = System.currentTimeMillis();
        pipeline.annotate(sentences);
        long duration = System.currentTimeMillis() - startTime;
        System.out.println(String.format(
                "Annotated %d sentences in %.02f seconds", sentences.size(), duration/1000.0
                ));

        // Output writer
        PrintWriter xmlOut = new PrintWriter("xmlOutput.xml");
        for(Annotation a: sentences) {
            pipeline.xmlPrint(a, xmlOut);
        }

        // Show some annotations
        for(Annotation a: sentences.subList(0,2)) {
            // Get token-wise annotations
            List<CoreLabel> tags = a.get(TokensAnnotation.class);
            if (tags == null) {
                System.out.println(String.format("%s: NO TAGS FOUND", a.toString()));
                continue;
            }

            System.out.println(a.get(TextAnnotation.class));
            for (CoreLabel tokenLabel : tags) {
                String text = tokenLabel.get(TextAnnotation.class);
                String tag = tokenLabel.get(PartOfSpeechAnnotation.class);
                System.out.println(String.format("    %s -> %s", text, tag));
            }
        }

        // Show available keys?
        Annotation a0 = sentences.get(0);
        System.out.println(a0.keySet().toString());
    }
}
