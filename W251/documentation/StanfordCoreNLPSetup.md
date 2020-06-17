# Setting up Stanford CoreNLP server for Sentiment Analysis via REST API
CoreNLP Version 3.9.1 website: https://stanfordnlp.github.io/CoreNLP/


Download the server distribution:

    wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip
	 unzip stanford-corenlp-full-2018-02-27.zip
	
Start the server (requires Java 8):

	 cd stanford-corenlp-full-2018-01-31
	 java -mx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000    

Install the python package:

	 pip install pycorenlp

Exercise the service with a python test:

    from pycorenlp import StanfordCoreNLP

    nlp = StanfordCoreNLP('http://localhost:9000')
    res = nlp.annotate("I love you. I hate him. You are nice. He is dumb",
                       properties={
                           'annotators': 'sentiment',
                           'outputFormat': 'json',
                           'timeout': 1000,
                       })
    for s in res["sentences"]:
        print("%d: '%s': %s %s" % (
            s["index"],
            " ".join([t["word"] for t in s["tokens"]]),
            s["sentimentValue"], s["sentiment"]))
            
result will be:

    0: 'I love you .': 3 Positive
    1: 'I hate him .': 1 Negative
    2: 'You are nice .': 3 Positive
    3: 'He is dumb': 1 Negative

