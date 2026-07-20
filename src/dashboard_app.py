import os
import re
from collections import Counter
from itertools import combinations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pymongo import MongoClient


st.set_page_config(page_title='Spotify Electronica Colombia', layout='wide')


STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'with', 'by', 'from', 'at',
    'de', 'la', 'el', 'y', 'o', 'del', 'los', 'las', 'un', 'una', 'en',
    'mix', 'remix', 'edit', 'version', 'original', 'radio', 'club', 'feat', 'ft', 'live', 'official'
}


def get_db():
    uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.environ.get('MONGODB_DB', 'spotify_electronica_colombia')
    client = MongoClient(uri)
    return client[db_name]


def load_data():
    db = get_db()
    return pd.DataFrame(list(db.analysis_tracks.find({}, {'_id': 0})))


def tokenize_text(text):
    if pd.isna(text) or not text:
        return []
    text = str(text).lower()
    tokens = re.findall(r"[a-záéíóúñü0-9]+", text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def text_frequencies(df):
    tokens = []
    for col in ['track_name', 'album_name']:
        if col in df.columns:
            for val in df[col].dropna().astype(str):
                tokens.extend(tokenize_text(val))
    return Counter(tokens)


def artist_frequency(df):
    counter = Counter()
    if 'artist_names' not in df.columns:
        return counter
    for arts in df['artist_names'].dropna():
        for a in arts:
            counter[a] += 1
    return counter


def top_album_frequency(df, n=12):
    if 'album_name' not in df.columns:
        return pd.DataFrame(columns=['album_name', 'tracks'])
    albums = df['album_name'].fillna('Unknown').value_counts().head(n).reset_index()
    albums.columns = ['album_name', 'tracks']
    return albums


def co_occurrence_pairs(df, n=20):
    pair_counter = Counter()
    for col in ['track_name', 'album_name']:
        if col not in df.columns:
            continue
        for val in df[col].dropna().astype(str):
            toks = sorted(set(tokenize_text(val)))
            for a, b in combinations(toks, 2):
                pair_counter[(a, b)] += 1
    rows = [{'source': a, 'target': b, 'weight': w} for (a, b), w in pair_counter.most_common(n)]
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def get_data():
    return load_data()


def style_fig(fig):
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    return fig


df = get_data()

st.title('Spotify Electronica Colombia')

if df.empty:
    st.warning('No hay datos en analysis_tracks.')
    st.stop()

if 'release_year' in df.columns:
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
if 'duration_min' in df.columns:
    df['duration_min'] = pd.to_numeric(df['duration_min'], errors='coerce')
if 'artist_count' in df.columns:
    df['artist_count'] = pd.to_numeric(df['artist_count'], errors='coerce')

with st.sidebar:
    st.header('Filtros')

    if 'release_year' in df.columns and df['release_year'].dropna().any():
        min_year = int(df['release_year'].dropna().min())
        max_year = int(df['release_year'].dropna().max())
        year_range = st.slider('Rango de años', min_year, max_year, (min_year, max_year))
        df = df[df['release_year'].between(year_range[0], year_range[1], inclusive='both')]

    if 'search_term' in df.columns:
        terms = sorted([t for t in df['search_term'].dropna().unique().tolist()])
        selected_terms = st.multiselect('Términos de búsqueda', terms, default=terms)
        if selected_terms:
            df = df[df['search_term'].isin(selected_terms)]

if df.empty:
    st.warning('No hay datos para los filtros seleccionados.')
    st.stop()

artist_counter = artist_frequency(df)
text_counter = text_frequencies(df)
collab_share = int((df['artist_count'].fillna(0) > 1).sum()) if 'artist_count' in df.columns else 0
single_share = int((df['artist_count'].fillna(0) <= 1).sum()) if 'artist_count' in df.columns else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric('Tracks', len(df))
k2.metric('Álbumes', df['album_id'].nunique(dropna=True) if 'album_id' in df.columns else 0)
k3.metric('Artistas únicos', len(artist_counter))
k4.metric('Duración prom.', f"{df['duration_min'].mean():.2f} min" if 'duration_min' in df.columns else 'NA')
k5.metric('Años', int(df['release_year'].dropna().nunique()) if 'release_year' in df.columns else 0)
k6.metric('Colaboraciones', collab_share)

left, right = st.columns(2)
with left:
    yearly = df.dropna(subset=['release_year']).groupby('release_year').size().reset_index(name='tracks')
    fig = px.line(yearly, x='release_year', y='tracks', markers=True)
    fig.update_layout(xaxis_title='Año', yaxis_title='Tracks')
    st.plotly_chart(style_fig(fig), use_container_width=True)

with right:
    terms = df['search_term'].fillna('unknown').value_counts().reset_index()
    terms.columns = ['search_term', 'tracks']
    fig = px.pie(terms, names='search_term', values='tracks', hole=0.45)
    st.plotly_chart(style_fig(fig), use_container_width=True)

left, right = st.columns(2)
with left:
    artists = pd.DataFrame(artist_counter.most_common(12), columns=['artist', 'tracks'])
    if not artists.empty:
        fig = px.treemap(artists, path=['artist'], values='tracks')
        st.plotly_chart(style_fig(fig), use_container_width=True)

with right:
    fig = px.histogram(df, x='duration_min', nbins=30)
    fig.update_layout(xaxis_title='Minutos', yaxis_title='Frecuencia')
    st.plotly_chart(style_fig(fig), use_container_width=True)

left, right = st.columns(2)
with left:
    collab_df = pd.DataFrame({
        'type': ['Solo', 'Colaboración'],
        'tracks': [single_share, collab_share]
    })
    fig = px.pie(collab_df, names='type', values='tracks', hole=0.5)
    st.plotly_chart(style_fig(fig), use_container_width=True)

with right:
    albums = top_album_frequency(df)
    if not albums.empty:
        fig = px.sunburst(albums, path=['album_name'], values='tracks')
        st.plotly_chart(style_fig(fig), use_container_width=True)

left, right = st.columns(2)
with left:
    top_words = pd.DataFrame(text_counter.most_common(20), columns=['word', 'count'])
    if not top_words.empty:
        fig = px.scatter(top_words, x='word', y='count', size='count', color='count', size_max=45)
        fig.update_layout(xaxis_title='Palabra', yaxis_title='Frecuencia')
        st.plotly_chart(style_fig(fig), use_container_width=True)

with right:
    pairs = co_occurrence_pairs(df, n=15)
    if not pairs.empty:
        labels = sorted(set(pairs['source']).union(set(pairs['target'])))
        idx = {label: i for i, label in enumerate(labels)}
        sankey = go.Figure(data=[go.Sankey(
            node=dict(label=labels, pad=12, thickness=16),
            link=dict(
                source=[idx[s] for s in pairs['source']],
                target=[idx[t] for t in pairs['target']],
                value=pairs['weight'].tolist()
            )
        )])
        st.plotly_chart(style_fig(sankey), use_container_width=True)

st.subheader('Muestra de datos')
st.dataframe(df.head(20), use_container_width=True)