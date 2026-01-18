import pandas as pd
import numpy as np

np.random.seed(42)
n_train = 500

train_data = pd.DataFrame({
    "age": np.random.randint(21, 65, size=n_train),
    "income": np.random.randint(20000, 120000, size=n_train),
    "loan_amount": np.random.randint(1000, 50000, size=n_train),
    "credit_score": np.random.randint(300, 850, size=n_train),
    "default": np.random.choice([0, 1], size=n_train, p=[0.8, 0.2])
})

train_data.to_csv("train_data.csv", index=False)
print("Sample training file 'train_data.csv' created!")

# Optional: sample prediction data
n_pred = 10
predict_data = pd.DataFrame({
    "age": np.random.randint(21, 65, size=n_pred),
    "income": np.random.randint(20000, 120000, size=n_pred),
    "loan_amount": np.random.randint(1000, 50000, size=n_pred),
    "credit_score": np.random.randint(300, 850, size=n_pred)
})

predict_data.to_csv("new_applicants.csv", index=False)
print("Sample prediction file 'new_applicants.csv' created!")
