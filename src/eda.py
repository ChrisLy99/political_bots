import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import ast

from collections import Counter
from wordcloud import WordCloud
from utils import get_project_root


root = get_project_root()
raw_data_path = os.path.join(root, 'data', 'raw', 'news')
json_data_path = os.path.join(root, 'data', 'processed', 'election')
graph_data_path = os.path.join(root, 'data', 'graphs', 'news')

def json_to_df(fp):
    """Reads in jsonl file and returns Pandas dataframe"""
    data = []
    with open(fp) as f:
        for line in f:
            data.append(json.loads(line))
            
    return pd.DataFrame(data)

def get_hashtags(df):
    """Returns a dictionary of hashtag occurences from dataframe of tweets"""
    
    def flatten(x):
        if len(x) != 0:
            return [d['text'] for d in x]
        else:
            return None
        
    inner_data = pd.json_normalize(df['entities'])
    hashtags = inner_data['hashtags'].apply(flatten)
    hashtags = hashtags.dropna()
    my_dict = Counter()

    for tag_list in hashtags:
        for tag in tag_list:
            my_dict[str.lower(tag)] +=1
    
    return my_dict

def count_hashtags(folder):
    """Returns dictionary of hashtag occurnces from all files in folder"""
    total_counter = Counter()
    

    for filename in os.listdir(folder):
        print('Parsing current file: ', filename)
        df = json_to_df(folder + '/' + filename)
        try:
            hashtags_dict = get_hashtags(df)
        except:
            continue

        total_counter += hashtags_dict

#     basedir = os.path.dirname(__file__)
#     fp = os.path.join(basedir, '..', 'data', 'out')

#     with open(fp + '/top_50_hashtags.txt', "w", encoding='utf-8') as f:
#         for k,v in  total_counter.most_common(50):
#             # print(k,v)
#             f.write( "{} {}\n".format(k,v) )
    return total_counter

def generate_word_cloud(counts, label):
    """Generates word cloud graph from dictionary of hashtag frequencies"""
    wordcloud = WordCloud(max_words=50, background_color="white")
    wordcloud.generate_from_frequencies(frequencies=counts)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(graph_data_path + '/' + label + '_wordcloud.png')

def main():
    for folder in os.listdir(raw_data_path):
        print(folder)
        counts = count_hashtags(raw_data_path + '/' + folder)
        generate_word_cloud(counts, folder)