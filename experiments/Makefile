.PHONY: train_logreg
train_logreg:
	mlflow run sklearn_logreg --run-name='logreg with bow' -P d=bow
	mlflow run sklearn_logreg --run-name='logreg with tfidf' -P d=tfidf
	mlflow run sklearn_logreg --run-name='logreg with fast_text' -P d=fast_text
	mlflow run sklearn_logreg --run-name='logreg with word_2_vec' -P d=word_2_vec
	mlflow run sklearn_logreg --run-name='logreg with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run sklearn_logreg --run-name='logreg with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run sklearn_logreg --run-name='logreg with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run sklearn_logreg --run-name='logreg with rubert_reviews_parsed' -P d=rubert_reviews_parsed
