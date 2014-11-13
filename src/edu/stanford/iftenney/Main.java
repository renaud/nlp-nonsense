package edu.stanford.iftenney;

import java.io.*;
import java.util.*;
import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.trees.TreeCoreAnnotations.*;
import edu.stanford.nlp.util.*;

import org.json.simple.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class Main {

    public static void main(String[] args) {
	    System.out.println("Hello World!");
        System.out.println("If you see this, I got the build system to work.");

        JSONParser jp = new JSONParser();
        String path = "/home/iftenney/afs/nlp-nonsense/data/";
        Object obj = null;
        try {
            EncodingFileReader fileReader = new EncodingFileReader(path + "test.txt.annotated");
            obj = jp.parse(fileReader);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        }
        JSONObject dataset = (JSONObject)obj;

        for (Object key : dataset.keySet()) {
            JSONArray ja = (JSONArray)dataset.get((String)key);
            String out = String.format("%s -> %s", ja.get(0), ja.get(1));
            System.out.println(out);
        }
        //System.out.println(dataset.keySet().toString());
    }
}
