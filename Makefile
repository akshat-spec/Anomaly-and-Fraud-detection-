.PHONY: install train evaluate mlflow-ui clean

install:
	pip install -r requirements.txt

train:
	python -m src.data.loader
	python -m src.features.engineer
	python -m src.models.anomaly
	python -m src.models.train

evaluate:
	python -m src.models.ensemble

mlflow-ui:
	mlflow ui --backend-store-uri sqlite:///mlflow.db

clean:
	rm -rf data/processed/*
	rm -rf models/*
	rm -rf mlruns/
	rm -f mlflow.db
