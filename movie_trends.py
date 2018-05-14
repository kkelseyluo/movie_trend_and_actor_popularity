from apikeys import TMDB_KEY
import requests
import datetime
import time
import bokeh.plotting as bplt
import bokeh
import calendar
import pandas as pd
from collections import OrderedDict

## Part I: Genres by Season

# make a list of genre number and name for the user feedback
def do_genre_list():
    genre_api=requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key='+TMDB_KEY+'&language=en-US')
    genres_api=genre_api.json()['genres']
    genre_list={}
    for i in genres_api:
        genre_list[i['id']]=i['name']
    return genre_list

# return the number of movies by genre in 2017
def get_release_amount(genre_list):
    print("\nIn the year of 2017:")
    print('{:10s}{:20s}{}'.format('ID','Genre','Number of Release'))
    for i in genre_list:
        genre=str(i)
        response=requests.get('https://api.themoviedb.org/3/discover/movie?api_key='+TMDB_KEY+'&language=en-US&sort_by=release_date.asc&include_adult=false&include_video=false&primary_release_year=2017&with_genres='+genre)
        print('{:10s}{:20s}{}'.format(str(i),genre_list[i],response.text.split(":")[2].split(',')[0]))

# Get moive list by genre by calling API
def do_movie_list(genre,genre_list):
    response=requests.get('https://api.themoviedb.org/3/discover/movie?api_key='+TMDB_KEY+'&language=en-US&sort_by=release_date.asc&include_adult=false&include_video=false&primary_release_year=2017&with_genres='+str(genre))
    TotalPage=int(response.text.split(":")[3].split(',')[0])
    movie_list=response.json()['results']
    for page in range(2,TotalPage+1):
        resp=requests.get('https://api.themoviedb.org/3/discover/movie?api_key='+TMDB_KEY+'&language=en-US&sort_by=release_date.asc&include_adult=false&include_video=false&primary_release_year=2017&with_genres='+str(genre)+'&page='+str(page))
        movie_list+=resp.json()['results']
    return movie_list
    
# Count number of release each month by ONE genre in the movie_list
def count_by_month(movie_list):
    count_by_month={}
    for i in range(1,13):
        count_by_month[str(i)]=0
    for item in movie_list:
        date=item['release_date']
        month=datetime.datetime.strptime(date,'%Y-%m-%d').month
        count_by_month[str(month)]+=1
    count_list=list(count_by_month.items())
    return count_list

# Call functions above one time for each genre to be plotted to get the plot data
def get_graph_data(genre_to_plot,genre_list):
    total_list=[]
    for g in genre_to_plot:
        total_list.append(count_by_month(do_movie_list(g,genre_list)))
    ylist=[]
    for i in range(len(genre_to_plot)):
        ylist.append([genre_list[int(genre_to_plot[i])],[j[1] for j in total_list[i]]])
        print('.')
    print("\nData collection completed, ready to do the visualization")
    return ylist

# visualization by using bokeh package
def visual_bok(ys):
    color=bokeh.palettes.mpl['Plasma'][5]
    bplt.output_file("genre_by_season.html")
    graph = bplt.figure(plot_width=800, plot_height=600,x_axis_label='Month',y_axis_label='Releases',title='Release by Genre: 2017')
    graph.title.text_font_size = '16pt'
    color_num=0
    for y in ys:
        graph.line(x=list(range(1,13)), y=y[1],line_width=4,legend=y[0],color=color[color_num])
        color_num+=1
        if color_num>=len(color):
            color_num=0
    graph.legend.orientation = "horizontal"
    # Set x ticks names
    month_name=[calendar.month_name[i][0:3] for i in range(1,13)]
    month_x={}
    for i in range(12):
        month_x[i+1]=month_name[i]
    graph.xaxis.major_label_overrides = month_x
    graph.xaxis[0].ticker.desired_num_ticks = 12
    
    graph.y_range.start = 0
    yss=[]
    # Set yrange_end larger so that legends won't be overlapped by the plot
    for i in ys:
        yss+=i[1]
    graph.y_range.end=max(yss)*1.2
    bplt.show(graph)

## Part II: Actor Popularity
### Huiru, please start code here, thank you.

## main functions
def assignment_1():
    default_list='37,10752,36,10770,14'
    # release_year=input('Please choose the year you want to explore the result here: ')
    genre_list=do_genre_list()
    get_release_amount(genre_list)
    print('\nPlease refer to the genre list above and choose the IDs to be plotted.')
    print('You can use default list :',default_list,'by hitting ENTER directly.')
    print('\n'+'*'*22,'NOTE', '*'*22)
    print('You might need to wait for longer time if you use')
    print('the IDs that have large number of releases.') 
    print('*'*22, "NOTE", '*'*22, '\n')
    genres=input('Please input genre IDs (divided by comma):')
    if genres=='':   
        genres=default_list
    genres=genres.split(',')
    print('\n'+'*'*52)
    print("It might take up to 1 minute to get all the data")
    print("Please wait for \"Data collection completed\" message")
    print('*'*52+'\n')
    visual_bok(get_graph_data(genres,genre_list))

def actor_chosen(actor_name):
    actor=actor_name.replace(" ", "+")
    actor_api=requests.get('http://api.tmdb.org/3/search/person?api_key='+TMDB_KEY+'&query='+str(actor))
    actor_api=actor_api.json()['results']
    actor_id=[d['id'] for d in actor_api]
    actor_id=actor_id[0]
    movie_api=requests.get('https://api.themoviedb.org/3/person/'+str(actor_id)+'/movie_credits?api_key='+TMDB_KEY+'&language=en-US')
    movie_api=movie_api.json()['cast']
    #print(movie_api)
    return movie_api

def movie_pop(movie_api):
	movie_profit=[]
	release_date=[]
	print("It might take up to 1 minute to get all the data")
	print("Please wait for \"Data collection completed\" message")
	print("Each dot represents one movie processed")
	for movie in movie_api:
		movie_data = requests.get('https://api.themoviedb.org/3/movie/'+ str(movie['id']) +'?api_key='+TMDB_KEY+'&language=en-US')
		movie_data = movie_data.json()
		if movie_data['revenue'] > 2000:
			movie_gross = movie_data['revenue']-movie_data['budget']
			movie_profit.append(movie_gross)
			release_date.append(movie_data['release_date'])
			print('.',sep=' ', end='', flush=True)
	print("\nData collection completed, ready to do the visualization")
	graph_data = dict(zip(release_date,movie_profit))
	graph_dict = OrderedDict(sorted(graph_data.items()))
	return graph_dict

def plot_pop(plot_dict,actor_name):
	x_sorted = list(plot_dict.keys())
	y = list(plot_dict.values())
	x = [datetime.datetime.strptime(i, "%Y-%m-%d") for i in x_sorted]
	df = pd.DataFrame({'date': x, 'popularity': y})
	bplt.output_file("actor_popularity.html")
	pop = bplt.figure(plot_width=800, plot_height=600,x_axis_type='datetime', x_axis_label='Year',y_axis_label='Profit',title=str(actor_name)+' Popularity over Time')
	pop.title.text_font_size = '16pt'
	pop.line(df['date'], df['popularity'], line_color='#2b8cbe')
	bplt.show(pop)

def assignment_2():
	actor_name=input("Please indicate which actor you want to analyze: ")
	movie_api=actor_chosen(actor_name)
	plot_dict=movie_pop(movie_api)
	plot_pop(plot_dict,actor_name)

def main():
    print('Hello! Please indicate which part of the assignment you want to see?')
    part=input('Please input 1 for \"Genres by Season\",  or 2 for \"Actor Popularity\" : ')
    if part=='1':
        assignment_1()
    elif part=='2':
        assignment_2()
    else:
        print('\n'+'*'*18, "ERROR", '*'*18)
        print(' I am sorry, but you can only input 1 or 2.')
        print('*'*18, "ERROR", '*'*18, '\n')
        main()

if __name__=="__main__":
    main()