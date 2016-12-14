import os
import numpy as np
import h5py
import pickle
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA

from flask import current_app

keys = None
features = None
nneighs = None

# def load_features(featuresfile):
#     keys, X = [], []
    
#     with h5py.File(featuresfile, 'r') as f:
#         for key in f.keys():
#             xx = f[key][...]
#             if np.any(np.isnan(xx)):
#                 print('{} has NaN values in {}'.format(key, featuresfile))
#                 continue
#             keys.append(int(key))
#             X.append(f[key][...])

#     return keys, np.array(X)

def load_features(featuresfile, perplexity=40):
    keys, X = [], []
    
    with h5py.File(featuresfile, 'r') as f:
        
        if 'tsne' in featuresfile:
            g = f['perplexity-{}'.format(perplexity)]
        else:
            g = f
            
        for key in g.keys():
            xx = g[key][...]
            keys.append(int(key))
            X.append(g[key][...])

    return keys, np.array(X)

def reload_features(featuresfile, keys, perplexity=40):
    X = []
    
    with h5py.File(featuresfile, 'r') as f:        
        if 'tsne' in featuresfile:
            g = f['perplexity-{}'.format(perplexity)]
        else:
            g = f
            
        for key in keys:
            xx = g[key][...]
            X.append(g[key][...])

    return np.array(X)


def build_search_tree(datadir, featurename='vgg16_block5_conv3-vlad-64.h5'):

    ndim = 64
    # features_file = 'vgg_pool5_vlad_64.h5'
    # features_file = os.path.join('mdb', 'static', 'features', features_file)
    features_file = os.path.join(datadir, 'data', 'full', 'features', featurename)
    print(features_file)
    
    global keys, features
    keys, features = load_features(features_file)

    print('reducing features')
    pca = PCA(n_components=ndim)
    features = pca.fit_transform(features)
    print('ready')

    print('building search tree')
    nn = NearestNeighbors()
    
    global nneighs
    nneighs = nn.fit(features)
    print('ready')

def query(entry_id):
    n_results = 16
    scikit_id = keys.index(entry_id)
    query_vector = features[scikit_id]
    scores, results = nneighs.kneighbors(query_vector, n_results)
    # result_entries = [keys[result] for result in results.flatten()]
    result_entries = map(keys.__getitem__, results.flatten())
    scores = ['{:0.4f}'.format(score) for score in scores.flatten()]

    return scores, result_entries

