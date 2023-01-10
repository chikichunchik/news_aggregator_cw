import joblib
import nltk
from model.transformer import Transformer
import os
import json



class Predictor:
    def __init__(self):
        os.chdir('..')
        with open('model/version.json') as f:
            versions = json.load(f)
        self.tfidf = joblib.load(versions['tfidf'])
        self.cv = joblib.load(versions['cv'])
        self.predictor = joblib.load(versions['predictor'])
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('stopwords')

    def predict(self, X):
        X = self.tfidf.transform(self.cv.transform(Transformer().transform(X)))
        result = self.predictor.predict(X)
        return result
