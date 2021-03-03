import pandas as pd
import numpy as np
import json

# Count the number of occurences of every hashtag in the JSON
def hashtag_counts(json_path):
#     print('in method')
    chunksize = 1
#     print('preparing reader....!')
    with open(json_path) as reader:
#         print('reader ready')
        ht_counts = dict({})
        for line in reader:
            hts = [h['text'] for h in json.loads(line)['entities']['hashtags']]
            for ht in hts:
                try:
                    ht_counts[ht] += 1
                except KeyError:
                    ht_counts[ht] = 0
#     print('finished calculating hashtag counts')
    return pd.Series(ht_counts)


# Count the number of posts every user has made in the JSON
def user_counts(json):
    df = pd.read_json(json, lines=True)
    us = df['user'].apply(lambda x: x['screen_name'])
    return us.value_counts()



# Count either hashtags or users in all available JSON files
def count_features(jsons, top_k = None, mode = 'hashtag'):
#     print('in count_features')
    # Decide whether to count hashtags or users
    if mode == 'hashtag':
        method = hashtag_counts
    elif mode == 'user':
        method = user_counts
        
    # Compile count of first JSON in list
    total_series = method(jsons[0])
#     print(f'vc shape {total_series.shape}')
    
    if len(jsons) > 1:
        # Append counts to every subsequent JSON
        for json in jsons[1:]:
            vc_series = method(json)
            total_series = total_series.add(vc_series, fill_value = 0)
#             print(f'vc shape {total_series.shape}')

    # Return the top users/hashtags in all of the data
    return total_series.sort_values().sort_values(ascending=False)