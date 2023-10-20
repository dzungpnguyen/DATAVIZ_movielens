import streamlit as st


def show_bloc(code, image):
    st.code(code, language='python')
    st.image(image)
    st.markdown('<br>', unsafe_allow_html=True)


def show_data():
    code = '''
            ratings = pd.read_csv('input/ratings.csv')
            movies = pd.read_csv('input/movies.csv')'''
    image1 = 'img/ratings.png'
    image2 = 'img/movies.png'
    st.code(code, language='python')
    st.image(image1)
    st.image(image2)
    st.markdown('<br>', unsafe_allow_html=True)


def show_merge():
    code = '''
        movies_ratings = movies.merge(ratings, on='movieId', how='inner')
        movies_ratings.month_year = movies_ratings.month_year.dt.to_timestamp()
        movies_ratings
            '''
    img = 'img/merge.png'
    show_bloc(code, img)


def show_transformations():
    st.write('First we create functions to get time element from the timestamp:')
    code1 = '''
        def get_weekday(dt):
            return dt.weekday()
        def get_hour(dt):
            return dt.hour
        def get_month_year(dt):
            return dt.to_period('M')
        '''
    st.code(code1, language='python')

    st.write('Now extracting to columns:')
    code1 = '''
        from datetime import datetime, timedelta
        ratings['start'] = datetime(1970,1,1,0,0,0)
        ratings['rating_date'] = pd.to_datetime(ratings['start']) + pd.to_timedelta(ratings['timestamp'], unit='s')
        ratings = ratings.drop(columns=['start'])

        ratings['weekday']= ratings['rating_date'].map(get_weekday)
        ratings['hour']= ratings['rating_date'].map(get_hour)
        ratings['month_year'] = ratings['rating_date'].map(get_month_year)
            '''
    img1 = 'img/trans1.png'
    show_bloc(code1, img1)    


def show_n_votes_per_rate():
    code = '''
        global_rating = pd.DataFrame(ratings['rating'].value_counts()).reset_index()
        global_rating.columns = ['index', 'rating']
        fig = px.pie(global_rating, values='rating', names='index',
                    title='Number of Votes for Each Rating Score',
                    labels={'index':'Rating Score','rating':'Number of Votes'},
                    color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(plot_bgcolor='black')
        fig.show()
        '''
    img = 'img/n-votes-per-rate.png'
    show_bloc(code, img)


def show_avg_rating_by_month():
    code = '''
        # create column average
        mr_avg_rating = movies_ratings.groupby(['month_year']).rating.mean()
        mr_avg_rating = mr_avg_rating.to_frame().reset_index()

        # plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mr_avg_rating.month_year, y=mr_avg_rating.rating,
                                mode='lines+markers', name='lines+markers'))
        fig.update_layout(title_text='Average Rating by Time',
                        xaxis_title='Month - Year',
                        yaxis_title='Rating',
                        title_x=0.5)
        fig.show()
            '''
    img = 'img/avg-rate-monthly.png'
    show_bloc(code, img)


def show_rating_freq():
    code = '''
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Weekday', 'Hour'))
        i = 1
        for feature in ['weekday','hour']:
            fig.add_trace(go.Histogram(x=movies_ratings[feature]), row=1, col=i)
            i += 1
        fig.update_layout(title_text='Rating Frequency by ...', bargap=0.3)
        fig.show()
            '''
    img = 'img/rate-freq.png'
    show_bloc(code, img)


def show_rating_density():
    code = '''
        mr_heatmap = movies_ratings.groupby(['weekday', 'hour']).size().unstack()
        fig = px.imshow(mr_heatmap, labels=dict(x="hour",y='weekday'),
                    y=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                    color_continuous_scale='RdBu_r')
        fig.layout.title = "Rating Density by Weekday and Hour"
        fig.show()
            '''
    img = 'img/rate-density.png'
    show_bloc(code, img)


def show_top_5_movies():
    code = '''
        fig = px.bar(movies_ratings.groupby(['title']).rating.size().sort_values(ascending=False).to_frame().reset_index()[:5],
                    x='title', y='rating', color='title', labels={'title':'Movie Title','rating':'Number of votes'},
                    title="Top 5 movies with highest number of votes")
        fig.show()
            '''
    img = 'img/top-movies.png'
    show_bloc(code, img)


def show_top_5_users():
    code = '''
        mr_5_users = movies_ratings.groupby(['userId']).rating.size().sort_values(ascending=False).to_frame().reset_index()
        mr_5_users['userId'] = mr_5_users['userId'].astype('str')
        fig = px.bar(mr_5_users[:5], x='userId', y='rating', color='userId',
                    labels={'userId':'User ID', 'rating':'Number of votes'},
                    title="Top 5 users voting the most")
        fig.show()
            '''
    img = 'img/top-users.png'
    show_bloc(code, img)


def show_avg_rating_top_5_movies():
    code = '''
        m1 = movies_ratings.title == 'Forrest Gump (1994)'
        m2 = movies_ratings.title == 'Shawshank Redemption, The (1994)'
        m3 = movies_ratings.title == 'Pulp Fiction (1994)'
        m4 = movies_ratings.title == 'Silence of the Lambs, The (1991) '
        m5 = movies_ratings.title == 'Matrix, The (1999)'
        mr_5_movies = movies_ratings[m1|m2|m3|m4|m5]
        mr_5_movies = mr_5_movies.groupby(['title','month_year']).rating.mean().to_frame().reset_index()

        fig = px.line(mr_5_movies, x='month_year', y='rating', color='title', symbol="title")
        fig.update_layout(title_text='Average Rating Score by Time - Top 5 Movies Voted the Most',
                        xaxis_title='Month - Year',
                        yaxis_title='Rating',
                        title_x=0.5)
        fig.show()
            '''
    img = 'img/avg-rate-top-movies.png'
    show_bloc(code, img)


def show_genre_ranking():
    code = '''
            # remove rows without 'genre'
            mr_cleaned = movies_ratings[movies_ratings.genres != '(no genres listed)']

            # list of genres
            composed_genres = mr_cleaned['genres'].unique().tolist()
            lst_genres = []
            grouped_genres = [genre.split('|') for genre in composed_genres]
            for genres in grouped_genres:
                for genre in genres:
                    if genre not in lst_genres:
                        lst_genres.append(genre)

            # count number of occurrences of each genre
            genres_count = pd.DataFrame()
            for genre in lst_genres:
                row = {'genre':genre,
                    'count':len(mr_cleaned[mr_cleaned['genres'].str.contains(genre)])}
                genres_count = genres_count.append(row, ignore_index=True)

            # plot
            fig = px.pie(genres_count, values='count', names='genre',
                        title='Genres Population Level',
                        labels={'genre':'Genre','count':'Number of occurrences'},
                        color_discrete_sequence=px.colors.sequential.deep)
            fig.show()
        '''
    img = 'img/genre-rank.png'
    show_bloc(code, img)

def main():
    st.title('Movielens Visual Interactive Exploration')

    st.markdown('''The objective of this application is to develop an interactive visual exploration process on
                the movielens dataset: https://grouplens.org/datasets/movielens/.
                <br><br>
                MovieLens dataset: GroupLens Research has collected and made available rating data sets from the MovieLens web site (https://movielens.org). The data sets were collected over various periods of time, depending on the size of the set.
                <br><br>
                Please review the README file for the usage details: https://files.grouplens.org/datasets/movielens/ml-25m-README.html
                <br><br>
                The dataset is available in this link : https://files.grouplens.org/datasets/movielens/ml-25m.zip''', unsafe_allow_html=True)
    
    st.header("Let's see our data!")
    show_data()

    st.header('Merge 2 datasets on movieId for later use')
    show_merge()

    st.header('Some data transformations on voting timestamp')
    show_transformations()

    st.header('Number of votes per rating score')
    show_n_votes_per_rate()

    st.header('Average rating by month')
    show_avg_rating_by_month()

    st.header('Rating frequency')
    show_rating_freq()

    st.header('Rating density by time')
    show_rating_density()

    st.header('Top 5 movies with highest votes')
    show_top_5_movies()

    st.header('Top 5 users voting the most')
    show_top_5_users()

    st.header('Average rating by time for top 5 movies')
    show_avg_rating_top_5_movies()

    st.header('Genre populcation ranking')
    show_genre_ranking()

if __name__ == '__main__':
    main()