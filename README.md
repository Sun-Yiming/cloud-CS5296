# Introduction


The ***\*searchLarge.py\**** file is the main program entrance, the first time run this file will create the index file whose name is ***\*corpus-large.\**** This process will cost majority time. 

 

The ***\*documents\**** directory is the file dataset. While the ***\*files\**** directory is some necessary files we will used in the main program. To be more specific, ***\*stopwords.txt\**** is the useless words we need to eliminate the words in the raw file. And the ***\*porter.py\**** is used to do the stem operation.

 

When you run the main program ***\*searchLarge.py\****, you need to enter your query on the commend. Then you can see the result like the graph below:

![img](https://github.com/Sun-Yiming/cloud-CS5296/blob/master/g1.png) 

 

The ***\*Clean.java\**** is the mapreduce program which is used to handle the raw files at the beginning stage.
