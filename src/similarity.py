import numpy as np
import pandas as pd
from src.stats import *
from sklearn.manifold import SpectralEmbedding

# takes in the hashtag vector from election, subsamples the hashtag space in usertime line with this vector
# election_hts: the ht vector
# user_timeline_fps: a list of file paths directing at user timeline jsons
def subsample_hashtags(election_hts:pd.Series, user_timeline_fps:list):
    user_hts = count_features(user_timeline_fps, top_k = None, mode='hashtag')
    subspaced_hts = user_hts.reindex(election_hts.index, fill_value=0)
    return subspaced_hts.values

# calculates the modified jaccard similarity of two hashtag vectors from two news stations
# precondition: the two vectors are of same dimension and the order of which follows the feature space
def jaccard_similarity(news_vec1: np.ndarray, news_vec2: np.ndarray):
    # just aliasing
    v1 = news_vec1
    v2 = news_vec2
    return np.sum(np.minimum(v1, v2)) / np.sum(np.maximum(v1, v2))


# takes in a list of file_paths towards folder for user timeline tweet for every news station
def construct_jaccard(news_stations:list):
    pass


# embed a graph by calculating laplacian eigenmap
def embed(affinity_matrix):
    pass
