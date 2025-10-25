# tests/test_train.py
import subprocess
import sys
import os
import time

def test_train_creates_model():
    # Run training
    rc = subprocess.call([sys.executable, "src/train.py"])
    assert rc == 0
    # Wait briefly for file system
    time.sleep(1)
    # Expect models/model-latest.joblib to exist
    assert os.path.exists("models/model-latest.joblib")
    # model_version.txt should exist
    assert os.path.exists("model_version.txt")
