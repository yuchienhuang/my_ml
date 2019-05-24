import numpy as np
import pandas as pd
import os
import json
from mymix.utils import *
import re


# Spotify API wrapper, documentation here: http://spotipy.readthedocs.io/en/latest/
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials



# Authenticate with Spotify using the Client Credentials flow
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials('d6967ce2057448d4aab3ad9898119c97',  'ad7f82cc26a64f1595b6b3c4cd917243')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



def track_json(track_id):
    d = spotify.track(track_id)
    subkeys = ['id', 'popularity', 'name', 'track_number']
    subdict = {k: d[k] for k in subkeys if k in d}
    return subdict


def audio_feature_decorator(spotify_audio_features_func):

    def wrapper_func(track_id_list):
        subkeys = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
        
        
        features_list = spotify_audio_features_func(track_id_list)
        
        my_features_list = []
        for i, features in enumerate(features_list):
            sub_features = {k: features[k] for k in subkeys if k in features}
            other_info = track_json(track_id_list[i])
            other_info.update(sub_features)
            
            my_features_list.append(other_info)
            
        return my_features_list
    
    return wrapper_func

@audio_feature_decorator
def audio_features(track_id_list):
    return spotify.audio_features(track_id_list)


def print_artists(ls):
    if len(ls) == 2:
        return ' & '.join(ls)
    else:
        return ', '.join(ls[:-1]) + ' & ' + ls[-1]

def get_data(album_json):
    
    tracks_df = pd.read_json(album_json['tracks_info'], orient='split')

    return {k: album_json[k] for k in ['id', 'name', 'genres', 'popularity', 'total_tracks', 'artists_list']}, tracks_df
    

def get_audio_link(album_id):
    return "https://open.spotify.com/track/" + album_id

def album_json(album_id):
    print('album_id: ',album_id)
    d = spotify.album(album_id)
    subkeys = ['id', 'name', 'genres',  'popularity', 'total_tracks']
    
    album_info = {k: d[k] for k in subkeys if k in d}
    tracks = d['tracks']['items']
    tracks_id = [t['id'] for t in tracks]
    tracks_df_json = pd.DataFrame(audio_features(tracks_id),columns=['id',  'track_number', 'popularity','name', 'duration_ms', 'tempo','time_signature', 'key',
       'valence', 'mode', 'acousticness', 'danceability', 'energy', 
       'instrumentalness',  'liveness', 'loudness', 'speechiness']).to_json(orient='split')
    album_info.update({'artists_list': [a['name'] for a in d['artists']], 'tracks_info': tracks_df_json })
    
    return album_info

def get_album_id_from_track(track, artists):
    try:
        track = track.replace("'",'')
        artists = ", ".join(re.split(r' & | x | X | With | with ', artists))
        q = 'track:' + track + ' artist:' + artists
        result = spotify.search(q, limit=1)
        the_first_album = result['tracks']['items'][0]['album']
        album_id = the_first_album.get('id')
        return album_id
    except:
#         try:
#             artists = ' '.join(artists.split(' x '))
#             artists = ' '.join(artists.split(' X '))
#             q = track + ' ' + artists
#             result = spotify.search(q, limit=1)
#             the_first_album = result['tracks']['items'][0]['album']
#             album_id = the_first_album.get('id')
#             return album_id
#         except:
        return track, artists

def get_album_id_from_album(album, artists):


    album = album.replace("'",'')        
    artists = ", ".join(re.split(r' & | x | X | With | with ', artists))
    q = 'album:' + album + ' artist:' + artists
    result = spotify.search(q, type='album', limit=1)
    the_first_album = result['albums']['items'][0]
    album_id = the_first_album.get('id')
    return album_id
    

def search_tracks(query):
    """
    This demo function will allow the user to search a song title and pick the song from a list in order to fetch
    the audio features/analysis of it
    :param spotify: An basic-authenticated spotipy client
    """
    
    selected_track = None

    search_term = query

        
    results = spotify.search(search_term)
    tracks = results.get('tracks', {}).get('items', [])
    return tracks

    


# def get_audio_features( tracks, tracks_artistnames):
def get_audio_features( tracks):
    """
    Given a list of tracks, get and print the audio features for those tracks!
    :param spotify: An authenticated Spotipy instance
    :param tracks: A list of track dictionaries
    """
    if not tracks:
        print('No tracks provided.')
        return

    
    #track_map = {track.get('id'): track for track in tracks}
    track_map = dict()
    tracks_artistnames=[]
    for track in tracks:
        track_map[track.get('id')] = track
        tracks_artistnames.append(track['artists'][0]['name'])

    # Request the audio features for the chosen tracks (limited to 50)
    
    tracks_features_response = spotify.audio_features(tracks=track_map.keys())

    desired_features = [
    'tempo',
    'time_signature',
    'key',
    'mode',
    'loudness',
    'energy',
    'danceability',
    'acousticness',
    'instrumentalness',
    'liveness',
    'speechiness',
    'valence'
    ]

    tracks_features_list = []
    for track_features in tracks_features_response:
        
        features_dict = dict()
        for feature in desired_features:
            
            feature_value = track_features.get(feature)

            
            if feature == 'key':
                feature_value = translate_key_to_pitch(feature_value)
            
            features_dict[feature] = feature_value
    
        tracks_features_list.append(features_dict)



    tracks_features_map = {f.get('id'): [tracks_artistnames[i], tracks_features_list[i], "https://open.spotify.com/track/" + f.get('id')] for i, f in enumerate(tracks_features_response)}

    
    
    
    
    

    return tracks_features_map



def translate_key_to_pitch(key):
    """
    Given a Key value in Pitch Class Notation, map the key to its actual pitch string
    https://en.wikipedia.org/wiki/Pitch_class
    :param key: The integer key
    :return: The translated Pitch Class string
    """
    pitches = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return pitches[key]