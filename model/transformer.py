import re
from nltk.stem import WordNetLemmatizer
import string
from nltk.corpus import stopwords
import nltk


class Transformer():
    def __init__(self):
        pass

    def transform(self, x):
        x = x.map(Transformer.__remove_punctuation)
        x = x.map(Transformer.__clean_text)
        x = x.map(Transformer.__lemmatizer)
        x = x.map(Transformer.__remove_stopwords)

        return x

    def fit(self, x, y):
        return self

    @staticmethod
    def __clean_text(text):
        text = text.lower()
        text = ' '.join(re.sub("(@[A-Za-z0-9]+)", " ", text).split())  # tags
        text = ' '.join(re.sub("^@?(\w){1,15}$", " ", text).split())

        text = ' '.join(re.sub("(\w+:\/\/\S+)", " ", text).split())  # Links
        text = ' '.join(re.sub("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", " ",
                               text).split())
        text = ' '.join(re.sub(r'http\S+', '', text).split())
        text = ' '.join(re.sub(r'www\S+', '', text).split())
        text = ' '.join(re.sub("\s+", " ", text).split())  # Extrem white Space
        text = ' '.join(re.sub("[^-9A-Za-z ]", "", text).split())  # digits
        text = ' '.join(re.sub('-', ' ', text).split())
        text = ' '.join(re.sub('_', ' ', text).split())  # underscore
        return text

    @staticmethod
    def __remove_stopwords(text):
        """The function to removing stopwords"""
        stop = stopwords.words('english')
        text = [word.lower() for word in text.split() if word.lower() not in stop]
        return " ".join(text)

    @staticmethod
    def __lemmatizer(text):
        """The function to apply lemmatizing"""
        word_list = nltk.word_tokenize(text)
        lemmatized_text = ' '.join([WordNetLemmatizer().lemmatize(w) for w in word_list])
        return lemmatized_text

    @staticmethod
    def __remove_punctuation(text):
        """The function to remove punctuation"""
        text = str(text)
        table = str.maketrans('', '', string.punctuation)
        return text.translate(table)
