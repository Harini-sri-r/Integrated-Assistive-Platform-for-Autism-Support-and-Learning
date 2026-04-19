import sys
import os

print(f"Python Version: {sys.version}")

try:
    print("Checking imports...")
    import flask
    print("✓ Flask imported")
    import flask_sqlalchemy
    print("✓ Flask-SQLAlchemy imported")
    import sqlalchemy
    print("✓ SQLAlchemy imported")
    import nltk
    print("✓ NLTK imported")
    import sklearn
    print("✓ Scikit-Learn imported")
    import numpy
    print("✓ Numpy imported")
    import scipy
    print(f"✓ Scipy imported (version: {scipy.__version__})")
    print("\nSUCCESS: All critical dependencies imported correctly.")
except ImportError as e:
    print(f"\nFAILURE: Missing dependency - {e}")
except Exception as e:
    print(f"\nCRITICAL HANG/ERROR: {e}")
