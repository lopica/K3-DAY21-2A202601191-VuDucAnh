import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class WineFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Them cac dac trung phai sinh tu domain knowledge ve hoa hoc ruou vang.
    Compatible voi sklearn Pipeline de co the luu/tai cung model.pkl.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            df = X.copy()
        else:
            raise ValueError("Input must be a pandas DataFrame")

        df['so2_ratio'] = df['free sulfur dioxide'] / (df['total sulfur dioxide'] + 1e-5)
        df['alc_density'] = df['alcohol'] / df['density']
        df['total_acidity'] = df['fixed acidity'] + df['volatile acidity']
        for col in ['residual sugar', 'chlorides', 'free sulfur dioxide', 'total sulfur dioxide']:
            df[f'log_{col.replace(" ", "_")}'] = np.log1p(df[col])

        return df
# trigger test Fri, Aug 21, 2026 12:13:17 PM
