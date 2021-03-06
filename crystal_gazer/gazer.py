import random
import os
import copy

import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import auc, roc_curve
from sklearn.preprocessing import LabelEncoder

from .sanitizer import cleanup_data


output_file = 'resources/results/predictions_on_test_data.csv'
noises = ['Bootcamp', 'S/N', 'Type', 'Joined Proctor on', 'Row']
non_num_cols = ['S/N', 'Bootcamp', 'Joined Proctor on']
target_cols = ['S/N', 'Score', '% Score', 'Bootcamp']
number = LabelEncoder()


class Gazer:
  def __init__(self):
    self.data = None
    self.x_train = None
    self.y_train = None
    self.y_train = None
    self.features = None
    self.roc_value = None
    self.classifier = None
    self.x_validate = None
    self.train_model()

  def train_model(self):
    self.data = self.get_dataframe_from_file()
    self.num_cols = list(set(list(self.data.columns)) - set(non_num_cols))
    self.data['Bootcamp'] = number.fit_transform(self.data['Bootcamp'].astype('str'))

    self.start_training()
    self.set_classifier()
    self.set_roc()

  def get_dataframe_from_file(self):
    file_path = 'resources/clean/andela_train_data.csv'
    return pd.read_csv(file_path)

  def generate_features(self):
    self.features = list(set(list(self.data.columns)) - set(noises))

  def start_training(self):
    self.data['is_train'] = np.random.uniform(0, 1, len(self.data)) <= .75

    Train = self.data[self.data['is_train'] == True]
    Validate = self.data[self.data['is_train'] == False]

    self.generate_features()
    self.x_train = Train[list(self.features)].values
    self.y_train = Train['Bootcamp'].values
    self.x_validate = Validate[list(self.features)].values
    self.y_validate = Validate['Bootcamp'].values

  def set_classifier(self):
    random.seed(100)
    random_forest = RandomForestClassifier(n_estimators=1000)
    random_forest.fit(self.x_train, self.y_train)
    self.classifier = random_forest

  def set_roc(self):
    status = self.get_status(self.x_validate)
    fpr, tpr, _ = roc_curve(self.y_validate, status[:,1], pos_label=1)
    self.roc_auc = auc(fpr, tpr)

  def get_status(self, data):
    return self.classifier.predict_proba(data)

  def get_prediction_for_data(self, data):
    data_df = pd.read_csv(data)
    sanitized_df = cleanup_data(data_df)
    csv = copy.deepcopy(sanitized_df)
    sanitized_df['is_train'] = [False for i in range(len(sanitized_df))]
    x_test = sanitized_df[list(self.features)].values
    verdict = self.get_status(x_test)
    sanitized_df["Bootcamp"] = verdict[:,1]
    return sanitized_df[target_cols], csv
