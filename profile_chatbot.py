import time
import sys

print("Starting profile...")
start = time.time()

import numpy as np
print(f"NumPy imported in {time.time() - start:.2f}s")
t = time.time()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
print(f"Sklearn imported in {time.time() - t:.2f}s")
t = time.time()

import nltk
print(f"NLTK imported in {time.time() - t:.2f}s")
t = time.time()

from chatbot import chatbot
print(f"Chatbot initialized in {time.time() - t:.2f}s")

print(f"Total time: {time.time() - start:.2f}s")
