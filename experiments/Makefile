.DEFAULT_GOAL := format
isort = isort .
black = black .
flake8  = flake8 .
pyupgrade = pyupgrade --py310-plus


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

.PHONY: train_svm
train_svm:
	mlflow run sklearn_svc --run-name='svm with bow' -P d=bow
	mlflow run sklearn_svc --run-name='svm with tfidf' -P d=tfidf
	mlflow run sklearn_svc --run-name='svm with fast_text' -P d=fast_text
	mlflow run sklearn_svc --run-name='svm with word_2_vec' -P d=word_2_vec
	mlflow run sklearn_svc --run-name='svm with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run sklearn_svc --run-name='svm with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run sklearn_svc --run-name='svm with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run sklearn_svc --run-name='svm with rubert_reviews_parsed' -P d=rubert_reviews_parsed

.PHONY: train_xgboost
train_xgboost:
	mlflow run xgboost_model --run-name='xgboost with bow' -P d=bow
	mlflow run xgboost_model --run-name='xgboost with tfidf' -P d=tfidf
	mlflow run xgboost_model --run-name='xgboost with fast_text' -P d=fast_text
	mlflow run xgboost_model --run-name='xgboost with word_2_vec' -P d=word_2_vec
	mlflow run xgboost_model --run-name='xgboost with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run xgboost_model --run-name='xgboost with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run xgboost_model --run-name='xgboost with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run xgboost_model --run-name='xgboost with rubert_reviews_parsed' -P d=rubert_reviews_parsed

.PHONY: train_forest
train_forest:
	mlflow run sklearn_forest --run-name='forest with bow' -P d=bow
	mlflow run sklearn_forest --run-name='forest with tfidf' -P d=tfidf
	mlflow run sklearn_forest --run-name='forest with fast_text' -P d=fast_text
	mlflow run sklearn_forest --run-name='forest with word_2_vec' -P d=word_2_vec
	mlflow run sklearn_forest --run-name='forest with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run sklearn_forest --run-name='forest with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run sklearn_forest --run-name='forest with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run sklearn_forest --run-name='forest with rubert_reviews_parsed' -P d=rubert_reviews_parsed

.PHONY: train_gradient
train_gradient:
	mlflow run sklearn_gradient --run-name='gradient with bow' -P d=bow
	mlflow run sklearn_gradient --run-name='gradient with tfidf' -P d=tfidf
	mlflow run sklearn_gradient --run-name='gradient with fast_text' -P d=fast_text
	mlflow run sklearn_gradient --run-name='gradient with word_2_vec' -P d=word_2_vec
	mlflow run sklearn_gradient --run-name='gradient with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run sklearn_gradient --run-name='gradient with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run sklearn_gradient --run-name='gradient with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run sklearn_gradient --run-name='gradient with rubert_reviews_parsed' -P d=rubert_reviews_parsed

.PHONY: train_catboost
train_catboost:
	mlflow run catboost_model --run-name='catboost with bow' -P d=bow
	mlflow run catboost_model --run-name='catboost with tfidf' -P d=tfidf
	mlflow run catboost_model --run-name='catboost with fast_text' -P d=fast_text
	mlflow run catboost_model --run-name='catboost with word_2_vec' -P d=word_2_vec
	mlflow run catboost_model --run-name='catboost with rubert_base_sentence' -P d=rubert_base_sentence
	mlflow run catboost_model --run-name='catboost with rubert_base_parsed' -P d=rubert_base_parsed
	mlflow run catboost_model --run-name='catboost with rubert_reviews_sentence' -P d=rubert_reviews_sentence
	mlflow run catboost_model --run-name='catboost with rubert_reviews_parsed' -P d=rubert_reviews_parsed

.PHONY: format
format:
	$(pyupgrade)
	$(isort)
	$(black)
	$(flake8)
