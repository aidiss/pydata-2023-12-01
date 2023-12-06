from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.preprocessing import Normalizer
import numpy as np


print("randomizer")
ct = make_column_transformer(
    (Normalizer(), make_column_selector(dtype_include=np.number)),
)
