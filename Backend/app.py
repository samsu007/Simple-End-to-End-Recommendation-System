import numpy as np
import pandas as pd
import tensorflow_datasets as tfds
import pprint
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from flask import Flask,jsonify,request,render_template,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Ratings data.
ratings = tfds.load("movielens/100k-ratings", split="train")
# Features of all the available movies.
movies = tfds.load("movielens/100k-movies", split="train")

df = tfds.as_dataframe(ratings)

"""
1. recommend movies based on ratings -> New User
2. item based recommendation using -> KNN
"""

based_on_ratings = df[['movie_title','user_rating','user_id','movie_id']]

# for byte conversion to string
def preprocessing(col):
  return based_on_ratings[col].map(lambda x : x.decode("utf-8"))

based_on_ratings['movie_title'] = preprocessing("movie_title")
based_on_ratings['user_id'] = preprocessing("user_id")
based_on_ratings['movie_id'] = preprocessing("movie_id")

based_on_ratings.head()

based_on_ratings.info()

based_on_ratings['user_rating'].value_counts()

# no of people watch each movies
def total_no_of_watchables(gr_col,tra_col,trans):
  return based_on_ratings.groupby(gr_col)[tra_col].transform(trans)

based_on_ratings['total'] = total_no_of_watchables(gr_col="movie_title",tra_col="movie_title",trans = "count")

based_on_items = df[['movie_title','user_rating','user_id','movie_id']]

def item_preprocessing(col):
  return based_on_items[col].map(lambda x : x.decode("utf-8"))

based_on_items['movie_title'] = item_preprocessing("movie_title")
based_on_items['user_id'] = item_preprocessing("user_id")
based_on_items['movie_id'] = item_preprocessing("movie_id")

based_on_items['user_id'] = based_on_items['user_id'].astype("int64")
based_on_items['movie_id'] = based_on_items['movie_id'].astype("int64")


pivot_view = based_on_items.pivot(index='movie_id',columns='user_id',values='user_rating')

pivot_view.fillna(0,inplace=True)
pivot_view.head()

min_voted_movie = 10
min_user_voted = 50

no_user_voted = based_on_items.groupby('movie_id')['user_rating'].agg('count')
no_movies_voted = based_on_items.groupby('user_id')['user_rating'].agg('count')


final_dataset =pivot_view.loc[:,no_movies_voted[no_movies_voted > min_user_voted].index]
final_dataset

# reduce the sparsity we use the csr_matrix function from the scipy library.
csr_data = csr_matrix(final_dataset.values)
final_dataset.reset_index(inplace=True)

knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
knn.fit(csr_data)


def new_user_recommendation(rat,wat):
  return based_on_ratings[(based_on_ratings['user_rating'] > rat) & (based_on_ratings['total'] >  wat)].sort_values(by="total",ascending=False)['movie_title'].unique()[0:8] 

def get_movie_recommendation(movie_name):
    top_movies = 4
    movie_list = based_on_items[based_on_items['movie_title'].str.contains(movie_name)]
    if len(movie_list):        
        movie_idx= movie_list.iloc[0]['movie_id']
        movie_idx = final_dataset[final_dataset['movie_id'] == movie_idx].index[0]
        distances , indices = knn.kneighbors(csr_data[movie_idx],n_neighbors=top_movies+1)
        rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
        recommend_frame = []
        for val in rec_movie_indices:
              movie_idx = based_on_items.iloc[val[0]]['movie_id']
              idx = based_on_items[based_on_items['movie_id'] == movie_idx].index
              recommend_frame.append({'Title':based_on_items.iloc[idx]['movie_title'].values[0],'Distance':val[1]})
        df = pd.DataFrame(recommend_frame,index=range(1,top_movies+1))
        return df
    else:
        return "No movies found. Please check your input"



@app.route('/',methods=['GET'])
def gettopmovies():
    abc = new_user_recommendation(4.0,200)
    return jsonify(
        movieslist=abc.tolist()
    )

@app.route('/',methods=['POST'])
def getrecommendedmovies():
    mtitle = request.json['mtitle']

    rec_mov = get_movie_recommendation(mtitle)

    print(rec_mov)
    return jsonify(
        rec_mov= rec_mov.values.tolist()
    )
    
   