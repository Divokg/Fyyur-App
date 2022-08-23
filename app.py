#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from config import DB_PATH
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = DB_PATH
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
from models import db, Venue, Artist, Show
db.init_app(app)
migrate = Migrate(app, db)
migrate.init_app(app)
                      
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  group_data = Venue.query.distinct( Venue.city, Venue.state).all()
  data=[]

  for _data in group_data:
    city_state = Venue.query.filter_by(state=_data.state).filter_by(city=_data.city).all()
    venue_info = []
    for venue in city_state:
      venue_info.append({
        'id':venue.id,
        'name':venue.name   
      }) 
    data.append({
      'city':_data.city,
      'state':_data.state,
      'venues':venue_info
    })
  return render_template('pages/venues.html', areas=data)

  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  
  data =[]
  for result in venues:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.Show
    })

  response= {
    "count": venues.count(),
    "data": data,
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)







@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  shows = {}

  upcoming  = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming:
   upcoming_shows.append({
      "artist_id":show.artist_id, 
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  past = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.artist_id==Artist.id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past:
    past_shows.append({
      "artist_id":show.artist_id, 
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
    

  shows = {
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_venue.html', venue=venue, shows=shows)
 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  formData = request.form
  new_venue = Venue(
                    name= formData['name'],
                    city=formData['city'],
                    state=formData['state'],
                    phone=formData['phone'],
                    address=formData.getlist('address'),
                    genres=formData.getlist('genres'),
                    facebook_link = formData['facebook_link'],
                    image_link = formData['image_link'],
                    website_link = formData['website_link'],
                    seeking_talent = bool(formData.get('seeking_talent')),
                    description = formData['seeking_description']
                    )
  try:  
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + formData['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured. Venue' + formData['name'] + 'could not be listed!')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(Venue.id == venue_id).delete()
        db.session.commit()
        flash('Success')
    except:
        db.session.rollback()
        flash('error')
    finally:
        db.session.close()
    return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

      artists=Artist.query.all()
    
      return render_template('pages/artists.html', artists=artists)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  
  data =[]
  for result in artists:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.Show
    })

  response= {
    "count": artists.count(),
    "data": data,
  }
  
 
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist=Artist.query.get(artist_id)
  

  upcoming  = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  
  upcoming_shows = []
  for show in upcoming:
   upcoming_shows.append({
      "venue_id":show.venue_id, 
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  past = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.venue_id==Venue.id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past:
    past_shows.append({
      "venue_id":show.venue_id, 
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
    

  shows = {
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_artist.html', artist=artist, shows=shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  formData = request.form
  artist = Artist.query.get(artist_id)
 
  artist.name= formData['name']
  artist.city=formData['city']
  artist.state=formData['state']
  artist.phone=formData['phone']
  artist.genres=formData.getlist('genres')
  artist.facebook_link = formData['facebook_link']
  artist.image_link = formData['image_link']
  artist.website_link = formData['website_link']
  artist.seeking_venue = bool(formData.get('seeking_venue'))
  artist.description = formData['seeking_description']
                  
  try:  
    
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + formData['name'] + ' was successfully Edited!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured . Artist ' + formData['name'] + ' could not be Edited!')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id, artist=artist))






@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.filter(Venue.id == venue_id).first()
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  formData = request.form
  venue = Venue.query.get(venue_id)
 
  venue.name= formData['name']
  venue.city=formData['city']
  venue.state=formData['state']
  venue.phone=formData['phone']
  venue.genres=formData.getlist('genres')
  venue.facebook_link = formData['facebook_link']
  venue.image_link = formData['image_link']
  venue.website_link = formData['website_link']
  venue.seeking_talent = bool(formData.get('seeking_talent'))
  venue.description = formData['seeking_description']
                  
  try:  
    
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + formData['name'] + ' was successfully Edited!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured . Venue ' + formData['name'] + ' could not be Edited!')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  formData = request.form
  new_artist = Artist(
                    name= formData['name'],
                    city=formData['city'],
                    state=formData['state'],
                    phone=formData['phone'],
                    genres=formData.getlist('genres'),
                    facebook_link = formData['facebook_link'],
                    image_link = formData['image_link'],
                    website_link = formData['website_link'],
                    seeking_venue = bool(formData.get('seeking_venue')),
                    description = formData['seeking_description']
                    )
  try:  
    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + formData['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured. Artist' + formData['name'] + 'could not be listed!')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  finally:
    db.session.close()
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by('start_time').all()

  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "artist_id": show.artist_id,
      "venue_name": show.venue.name,
      "artist_name":show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)


#------------------------------------------------------------------------------------------------------------------------------------------


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  formData = request.form
  new_show = Show(
                    artist_id= formData['artist_id'],
                    venue_id=formData['venue_id'],
                    start_time=formData['start_time']                    
                    )
  try:  
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured.')
    # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')



  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:

if __name__ == '__main__':
   app.debug = True
   app.run(host="0.0.0.0")


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''