# About
How does the language of legal doctrine shape judicial opinion-writing? This code provides a framework for training NLP models to generate a unidimensional "scrutiny scale" (i.e., scaling along the different levels of the tiers-of-scrutiny doctrine). It then scores free expression opinions along that scale and performs some initial hypothesis testing regarding the relationship between scrutiny and judicial ideology. See below for specific replication steps.

# Replication
## Corpus acquisition and preprocessing
1. Opinion files are obtained from LexisNexis. Run this `R` script to generate well-formed search queries, manually feed those queries into the LexisNexis interface (no API access), and finally download the returned documents as zipped `.rtf` files.
	
	```
	Rscript scaling/generate_lexisnexis_queries.R
	```

2. Place the raw `.rtf` files in the `/data/corpus/raw/` subdirectories as follows:

	```
	/data/corpus
		├── archives **.zip archives from LexisNexis**
		├── preprocessed **output from the preprocessor**
		└── raw
			├── cb **content-based**
			├── cn **content-neutral**
			├── lp **less-protected**
			└── nm **not-met**
	```

3. Convert the `.rtf` files to `.txt` files using `textutil`.

	```
	textutil -convert txt *.rtf
	rm *.rtf
	```

4. Remove the following duplicate opinions manually (for some reason LexisNexis sometimes returns concurring/dissenting opinions separately).

	```
	Int'l Soc'y for Krishna Consciousness v. Lee, 505 U.S. 672(2).txt
	Bd. of County Comm'rs v. Umbehr, 518 U.S. 668.txt
	```

5. Pre-process the corpus. (Extract the majority opinion from each `.txt` file; tokenize it into paragraphs, sentences, and words; tag each word with its part of speech tag; and save the opinion as a `.pickle` file for future consumption.)

	```
	python3
	
	from preprocessing import Preprocessor
	Preprocessor().process()
	```


## Model training and score generation
Broadly, two different species of models can be trained: Classification models and regression models. Set the specific model name in `training.py` as an element in the `self.classifiers` list for the appropriate `ModelTrainer` class. To train multiple models at once, simply add multiple classifiers to that list.

1. To train a classification model:

	```
	python3
	
	from training import ClassificationModelTrainer

	model_trainer = ClassificationModelTrainer()
	model_trainer.train()
	```

2. To train a regression model:

	```	
	from training import RegressionModelTrainer

	model_trainer = RegressionModelTrainer()
	model_trainer.train()
	```

3. To perform k-fold cross-validation and pretty-print the results:

	```
	print(model_trainer.validate())
	```

4. To save the trained model and its entire pipeline to disk:

	```
	model_trainer.save()
	```

Score generation follows a similar process. Because scores are generated differently for classification and regression models, make sure to instantiate the appropriate `Scorer` class. Simply pass the model name (a timestamped version of the classifier name, as saved to disk) as its first argument.

1. To generate scores for a classification model:

	```
	python3
	
	from scoring import ClassificationScorer
	
	s = ClassificationScorer(MODEL_NAME) # e.g., ClassificationScorer('LinearSVC-1557173364.336978')
	s.score()
	```

2. To generate scores for a regression model:

	```	
	from scoring import RegressionScorer
	
	s = RegressionScorer(MODEL_NAME)
	s.score()
	```

3. To save the scores to disk:

	```
	s.save()
	```

## Hypothesis testing
1. With the scrutiny scores in hand, it is now possible to do meaningful hypothesis testing. First, make sure the data from Richards and Kritzer has been properly normalized:

	```
	Rscript analysis/normalize_rk_data.R
	```

2. Then, join their data with the generated scrutiny scores and some other variables:

	```
	Rscript analysis/join_fe_data.R
	```

3. Finally, perform hypothesis testing. (As of now, only some simple linear regressions.)

	```
	Rscript analysis/test.R
	```

4. Optionally, create some visualizations:

	```
	Rscript analysis/create_figures.R
	```