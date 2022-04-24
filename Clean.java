package project;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import wordcount.Problem1;

import java.io.IOException;

public class Clean {
    private final static String[] stopWords = {"a", "about", "above", "across", "adj", "after", "again", "against",
            "all", "almost", "alone", "along", "also", "although", "always", "am", "among", "an", "and", "another",
            "any", "anybody", "anyone", "anything", "anywhere", "apart", "are", "around", "as", "aside", "at", "away",
            "be", "because", "been", "before", "behind", "being", "below", "besides", "between", "beyond", "both",
            "but", "by", "can", "cannot", "could", "deep", "did", "do", "does", "doing", "done", "down", "downwards",
            "during", "each", "either", "else", "enough", "etc", "even", "ever", "every", "everybody", "everyone",
            "except", "far", "few", "for", "forth", "from", "get", "gets", "got", "had", "hardly", "has", "have",
            "having", "her", "here", "herself", "him", "himself", "his", "how", "however", "i", "if", "in", "indeed",
            "instead", "into", "inward", "is", "it", "its", "itself", "just", "kept", "many", "maybe", "might", "mine",
            "more", "most", "mostly", "much", "must", "myself", "near", "neither", "next", "no", "nobody", "none",
            "nor", "not", "nothing", "nowhere", "of", "off", "often", "on", "only", "onto", "or", "other", "others",
            "ought", "our", "ours", "out", "outside", "over", "own", "p", "per", "please", "plus", "pp", "quite",
            "rather", "really", "said", "seem", "self", "selves", "several", "shall", "she", "should", "since", "so",
            "some", "somebody", "somewhat", "still", "such", "than", "that", "the", "their", "theirs", "them",
            "themselves", "then", "there", "therefore", "these", "they", "this", "thorough", "thoroughly", "those",
            "through", "thus", "to", "together", "too", "toward", "towards", "under", "until", "up", "upon", "v",
            "very", "was", "well", "were", "what", "whatever", "when", "whenever", "where", "whether", "which", "while",
            "who", "whom", "whose", "will", "with", "within", "without", "would", "yet", "young", "your", "yourself"};

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(Clean.class);
        job.setMapperClass(Clean.myMapper.class);
        job.setCombinerClass(Clean.myReducer.class);
        job.setReducerClass(Clean.myReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

    public static class myMapper extends Mapper<Object, Text, Text, IntWritable> {
        private static final IntWritable one = new IntWritable(1);
        public void map(Object key, Text value, Mapper<Object, Text, Text, IntWritable>.Context context)
                throws IOException, InterruptedException {
            String[] split = value.toString().split("\\s+");
            Text text = new Text();
            for (String word:split){
                for(String token:stopWords){
                    if (!word.contains(token)){
                        text.set(token);
                        context.write(text,one);
                    }
                }
            }

        }
    }

    public static class myReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
        private IntWritable result = new IntWritable();
        public void reduce(Text key, Iterable<IntWritable> values, Reducer<Text, IntWritable, Text, IntWritable>.Context context)
                throws IOException, InterruptedException {
            int sum = 0;
            for(IntWritable intWritable:values) {
                sum += intWritable.get();
            }
            this.result.set(sum);
            context.write(key, this.result);
        }
    }
}
