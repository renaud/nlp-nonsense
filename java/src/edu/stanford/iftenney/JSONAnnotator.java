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

/**
 * Created by iftenney on 11/15/14.
 */

public class JSONAnnotator {

    public static class CustomFulltextAnnotation implements CoreAnnotation<String> {
        public Class<String> getType() {
            return String.class;
        }
    }

    public static class CustomLabelAnnotation implements CoreAnnotation<String> {
        public Class<String> getType() {
            return String.class;
        }
    }

    public static class CustomGUIDAnnotation implements CoreAnnotation<String> {
        public Class<String> getType() {
            return String.class;
        }
    }

    // Extract tag lists from a list of CoreLabel tokens
    public static List<String> getTagList(List<CoreLabel> tokens, Class<? extends TypesafeMap.Key<String>> key) {
        List<String> taglist = new ArrayList<>();
        for (CoreLabel token : tokens) {
            taglist.add(token.get(key));
        }
        return taglist;
    }

    public static void main(String[] args) throws IOException {
        String infile = args[0];

        // Load data from JSON
        JSONParser jp = new JSONParser();
        Object obj = null;
        try {
            EncodingFileReader fileReader = new EncodingFileReader(infile);
            obj = jp.parse(fileReader);
        } catch (ParseException e) {
            System.out.printf("Error type: %d%n", e.getErrorType());
            System.out.printf("Position: %d%n", e.getPosition());
            System.out.printf("Unexpected: %s%n", e.getUnexpectedObject());
            e.printStackTrace();
            System.exit(1);
        }
        JSONObject dataset = (JSONObject)obj;

        // Make list of sentences
        List<Annotation> sentences = new ArrayList<>(dataset.size());
        for (Object key : dataset.keySet()) {
            String guid = (String)key;
            JSONArray ja = (JSONArray)dataset.get(guid);

            Annotation a = new Annotation((String)ja.get(0));
            a.set(CustomGUIDAnnotation.class, guid); // store ID
            a.set(CustomFulltextAnnotation.class, (String)ja.get(0)); // store unmodified fulltext

            JSONArray labels = null;
            try {
                labels = (JSONArray)ja.get(1);
            } catch (ClassCastException e) {
                labels = new JSONArray();
                labels.add(ja.get(1));
                //labels.put(ja.get(1));
            }
            a.set(CustomLabelAnnotation.class, labels.toString()); // store custom label
            // a.set(CustomLabelAnnotation.class, (String)ja.get(1)); // store custom label
            sentences.add(a);

            //String out = String.format("%s -> %s", ja.get(0), ja.get(1));
            //System.out.println(out);
        }

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
        //PrintWriter jsonOut = new PrintWriter(infile+".tagged.json");
        //for(Annotation a: sentences) {
        //    pipeline.jsonPrint(a, jsonOut);
        //}

        // Generate compact JSON representation
        String outfile = infile+".tagged.json";
        PrintWriter jsonOut = new PrintWriter(outfile);
        int counter = 0;
        for (Annotation a: sentences) {
            JSONObject jobj = new JSONObject();

            List<CoreLabel> tokens = a.get(TokensAnnotation.class);
            jobj.put("word",getTagList(tokens, TextAnnotation.class));
            jobj.put("lemma", getTagList(tokens, LemmaAnnotation.class));
            jobj.put("pos", getTagList(tokens, PartOfSpeechAnnotation.class));
            jobj.put("ner", getTagList(tokens, NamedEntityTagAnnotation.class));
            jobj.put("__LABEL__", a.get(CustomLabelAnnotation.class));
            jobj.put("__ID__", a.get(CustomGUIDAnnotation.class));
            jobj.put("__TEXT__", a.get(CustomFulltextAnnotation.class));

            System.out.println("Writing tagged sentence " + a.get(CustomGUIDAnnotation.class));

            String json = jobj.toJSONString() + "\n";
            jsonOut.write(json);
            jsonOut.flush();
            counter++;
        }

        System.out.println(String.format("Wrote %d sentences to %s", counter, outfile));

    }

}
