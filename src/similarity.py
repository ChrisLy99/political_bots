import numpy as np
import pandas as pd
from src.hashtags import *
import matplotlib.pyplot as plt
import os
import json
from sklearn.manifold import SpectralEmbedding

def uncase_hashtags(vector):
    vector.index= vector.index.str.lower()
    new_vec = vector.reset_index().groupby('index').sum()[0].sort_values(ascending=False)
    return new_vec

def normalize_counts(vector):
    return vector / vector.sum()

# choosing this over regex because regex overexcludes options
def remove_covid(vector, covid_keywords):
    return vector.loc[~vector.index.isin(covid_keywords)]

# takes in the hashtag vector from election, subsamples the hashtag space in usertime line with this vector
# election_hts: the ht vector
# user_timeline_fps: a list of file paths directing at user timeline jsons
def subsample_hashtags(election_hts:pd.Series, user_timeline_fps:list):
    '''
    takes in the hashtag vector from election, subsamples the hashtag space in usertime line with this vecto
    
    Parameters
    ----------
    election_hts : pd.Series
        a dictionary with keys to be news_station names and values to be hashtag count vectors.
        
    user_timeline_fps : str
        the list of filepaths that refers to timeline files of one news station
        
    normalize: boolean
        passed in from the caller function compile_vectors, decides whether to normalize the hashtag counts

    Returns
    -------
    count_vector : np.ndarray
        an array of the counts of the hashtag space
   
    
    '''
    print('in subsample')
    user_hts = count_features(user_timeline_fps, top_k = None, mode='hashtag')
    subspaced_hts = user_hts.reindex(election_hts.index, fill_value=0)
    return subspaced_hts.values


# timeline_fp: 
def compile_vectors(timeline_fp, vector:pd.Series, case_sensitive=False, normalize=True, kws=None):
    '''
    takes in the folder that contains user timeline jsons, constructs a dictionary with keys of news_station names 
    and values of the hashtag vectors
    
    Parameters
    ----------
    timeline_fp : str
        path that contains {news_station}_{number}_users.jsonl
        
    vector : pd.Series
        a pandas series object that is the value counts of the hashtag space from election dataset

    Returns
    -------
    result : dict
        a dictionary with keys of news_station names and values of the hashtag vectors
    '''
    if not case_sensitive:
        print('uncasing hashtags')
        vector = uncase_hashtags(vector.copy())
    if normalize:
        print('normalizing hashtags')
        vector = normalize_counts(vector.copy())
    if kws is not None:
        print('removing keywords')
        vector = remove_covid(vector.copy(), kws)
    files = [os.path.join(timeline_fp, file) for file in os.listdir(timeline_fp) if 'users.jsonl' in file]
    result = {}
    for f in files:
        news_station = os.path.split(f)[1].split('_')[0]
        print(f)
        # ugly, but had to comply with the hashtag collection function :p
        user_jsons = [f]
        # calculate the vector for this news station
        ht_vector = subsample_hashtags(vector, user_jsons)
        result[news_station] = ht_vector
    return result


# calculates the modified jaccard similarity of two hashtag vectors from two news stations
# precondition: the two vectors are of same dimension and the order of which follows the feature space
def jaccard_similarity(news_vec1: np.ndarray, news_vec2: np.ndarray):
    # just aliasing
    v1 = news_vec1
    v2 = news_vec2
    result = 1 - np.sum(np.minimum(v1, v2)) / np.sum(np.maximum(v1, v2))
#     print(np.minimum(v1, v2), np.maximum(v1, v2))
    return result


def construct_jaccard(news_vectors:dict):
    '''
    constructs the nxn adjacency matrix (affinity matrix) from the result of function compile_vectors() 
    
    Parameters
    ----------
    news_vectors : dict
        a dictionary with keys to be news_station names and values to be hashtag count vectors.

    Returns
    -------
    news : list
        the order of news stations from after which the index of matrix follows
    
    adjacency : np.ndarry
        the adjacency matrix
    
    '''
    news = list(news_vectors.keys())
    n_news = len(news)
    adjacency = np.zeros((len(news), len(news)))
    # O(n^2) is bnd but we don't have a lot of news stations.
    for r in range(adjacency.shape[0]):
        for c in range(adjacency.shape[1]):
            news1 = news[r]
            news2 = news[c]
#             if news1 == news2:
#                 adjacency[r][c] = 1
#             else:
            adjacency[r][c] = jaccard_similarity(news_vectors[news1], news_vectors[news2])
    
    return news, adjacency


# embed a graph by calculating laplacian eigenmap
def embed(affinity_matrix, n = 1):
    '''
    uses SpectralEmbedding class from sklearn to calculate the laplacian eigenmap.
    
    Parameters
    ----------
    affinity_matrix : np.ndarray
        a dictionary with keys to be news_station names and values to be hashtag count vectors.

    Returns
    -------
    vectors: list
        a list of n-d coordinates for each news station. couple this with the news vector from the first return of 
        construct_jaccard to plot meaningful graphs
    
    '''
    lap_eigenmap = SpectralEmbedding(n, affinity='precomputed')
    return lap_eigenmap.fit_transform(affinity_matrix)

# execute the entire similarity process and plots the resultant graph
def plot_embedding(timeline_fp, vector, save_path, dim=1, case_sensitive=False, normalize=True, kws=None):
    news_vectors = compile_vectors(timeline_fp, vector, case_sensitive=case_sensitive, normalize=normalize, kws=kws)
    to_save = {}
    for key in news_vectors.keys():
        to_save[key] = news_vectors[key].tolist()
    json.dump(to_save, open(save_path, 'w'))
    news, adjacency = construct_jaccard(news_vectors)
    results = embed(adjacency, n=dim)
    if dim < 2:
        for i in range(len(results)):
            coord = results[i]
            plt.scatter(*[coord,0], label = news[i])
        plt.title('dimensional reduction of the graph')
        plt.legend()
    else:
        for i in range(len(results)):
            coord = results[i]
            plt.scatter(*coord, label = news[i])
        plt.title('dimensional reduction of the graph')
        plt.legend()

