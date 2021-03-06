from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)

from flask_debugtoolbar import DebugToolbarExtension

from model import (User, Movie, Color, Ensemble, Top, Bottom, Accessory, Shoe, Dress, Bag, Cache, connect_to_db, db)

from passlib.hash import sha256_crypt

import etsy

import random

import re

app = Flask(__name__)

connect_to_db(app)


# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def show_home_page():
    """Show home page."""
    return render_template('homepage.html')

@app.route('/nav')
def nav_bar():
    """testing purpose"""
    return render_template('nav.html', 
                            user_id=session.get('logged_in'),
                            logged_in=bool(session.get('logged_in')))

@app.route('/register', methods=["GET", "POST"])
def register_page():
    """Register user."""

    profile_pic = ["/static/css/images/profile_pic/gustav.jpg",
                    "/static/css/images/profile_pic/zero.jpg",
                    "/static/css/images/profile_pic/mrjean.jpg",
                    "/static/css/images/profile_pic/agatha.jpg",
                    "/static/css/images/profile_pic/henckels.jpg",
                    "/static/css/images/profile_pic/dmitri.jpg",
                    "/static/css/images/profile_pic/sam.jpg",
                    "/static/css/images/profile_pic/suzy.jpg",
                    "/static/css/images/profile_pic/walt.jpg",
                    "/static/css/images/profile_pic/ben.jpg",
                    "/static/css/images/profile_pic/francis.jpg",
                    "/static/css/images/profile_pic/peter.jpg",
                    "/static/css/images/profile_pic/jack.jpg",
                    "/static/css/images/profile_pic/margot.jpg",
                    "/static/css/images/profile_pic/richard.jpg",
                    "/static/css/images/profile_pic/elicash.jpg",
                    "/static/css/images/profile_pic/royal.jpg",
                    "/static/css/images/profile_pic/etheline.jpg",
                    "/static/css/images/profile_pic/chas.jpg",
                    "/static/css/images/profile_pic/henry.jpg",
                    "/static/css/images/profile_pic/pagoda.jpg",
                    "/static/css/images/profile_pic/stevezissue.jpg",
                    "/static/css/images/profile_pic/ned.jpg",
                    "/static/css/images/profile_pic/klaus.jpg",
                    "/static/css/images/profile_pic/eleanor.jpg",
                    "/static/css/images/profile_pic/max.jpg",
                    "/static/css/images/profile_pic/dignan.jpg"]

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = sha256_crypt.encrypt((str(request.form.get("password"))))
        pic = random.choice(profile_pic)
        print "pic_url", pic
        email_re = re.search(r".+@.+\..+", email)  # email validation
        username_re = re.search(r"[^@]+", username)

        if not username_re:
            flash("Username can not contain '@' sign.")
            return rediect("/search")

        if not email_re:
            flash("Please use legal email format.")
            return rediect("/search")

        if User.query.filter(User.username == username).first():
            flash("That username is already taken, please choose another one.")
            return rediect("/search")
   
        # flash("Thanks for registering!")
        new_user = User(username=username, email=email, password=password, pic=pic)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = new_user.id

        return redirect('/search')

    else:
        return rediect("/search")


# @app.route('/login')
# def show_login_form():
#     """Show login form."""
#     return render_template('log_in.html')


@app.route('/login', methods=['POST'])
def process_form():
    """Validate user login info."""

    login = request.form.get('login')
    password = request.form.get('password')

    user = User.query.filter((User.email == login) | (User.username == login)).first()

    # if not user or if user is None:
    if not user:
        flash('Username or email not recognized, try again.')
        return redirect('/search')

    elif user.password != password:
        flash('Password is wrong, please log in again')
        return redirect('/search')

    else:
        session['logged_in'] = user.id
        flash('Log in successful!')
        return redirect('/users/' + str(user.id))


@app.route('/logout')
def logout():
    """Log out user."""
    if 'logged_in' in session:
        del session['logged_in']
    if 'movie' in session:
        del session['movie']
    # flash("You have been logged out.", "success")

    return redirect("/search")


@app.route('/users/<user_id>')
def show_user_profile(user_id):
    """Show user profile page."""
    # check if the logged in user has permission to view the user profile page
    if int(user_id) != session.get('logged_in'):
        return redirect("/search")

    print user_id
    user = User.query.filter(User.id == user_id).one()
    email = user.email
    pic = user.pic
    username = user.username

    ensembles = user.ensembles

    points_per_ensemble ={}
    points = 0
    for ea in user.ensemble_associations:
        points += ea.points
        points_per_ensemble[ea.ensemble] = ea.points

    # if points:
    #     flash("You got a point!")

    movie_ensemble = {}
    for ensemble in ensembles:
        ensemble_points_pair = (points_per_ensemble.get(ensemble, 0), ensemble)
        if ensemble.movie not in movie_ensemble:
            movie_ensemble[ensemble.movie] = [ensemble_points_pair]
        else:
            movie_ensemble[ensemble.movie].append(ensemble_points_pair)

    for pair_lst in movie_ensemble.values():
        pair_lst.sort(reverse=True)

    return render_template('user_profile.html',
                            pic=pic,
                            email=email,
                            username=username,
                            ensembles=ensembles,
                            movie_ensemble=movie_ensemble,
                            points=points,
                            )


@app.route('/ensembles', methods=['POST'])
def save_ensemble():
    """User saved ensembles."""
    top_listing = request.form.get("top_listing")
    bottom_listing = request.form.get("bottom_listing")
    accessory_listing = request.form.get("accessory_listing")
    shoe_listing = request.form.get('shoe_listing')
    bag_listing = request.form.get('bag_listing')
    dress_listing = request.form.get('dress_listing')
    movie_id = request.form.get('movie_id')
    
    accessory_img_url = request.form.get('a_img_url')
    top_img_url = request.form.get('t_img_url')
    bottom_img_url = request.form.get('bo_img_url')
    shoe_img_url = request.form.get('s_img_url')
    bag_img_url = request.form.get('b_img_url')
    dress_img_url = request.form.get('d_img_url')

    user_id = session['logged_in']
    user = User.query.filter(User.id == user_id).one()


    def find_or_add(itemClass, l_url, img_url):
            item = itemClass.query.filter(itemClass.listing_url == l_url).first()
            if not item:
                item = itemClass(listing_url=l_url,
                        img_url=img_url)
                db.session.add(item)

            return item


    top = find_or_add(Top, top_listing, top_img_url)
    accessory = find_or_add(Accessory, accessory_listing, accessory_img_url)
    bottom = find_or_add(Bottom, bottom_listing, bottom_img_url)
    shoe = find_or_add(Shoe, shoe_listing, shoe_img_url)
    bag = find_or_add(Bag, bag_listing, bag_img_url)
    dress = find_or_add(Dress, dress_listing, dress_img_url)

    db.session.commit()

    ensemble = Ensemble.query.filter(Ensemble.top_id == top.id,
                                     Ensemble.bottom_id == bottom.id,
                                     Ensemble.accessory_id == accessory.id,
                                     Ensemble.shoe_id == shoe.id,
                                     Ensemble.bag_id == bag.id,
                                     Ensemble.dress_id == dress.id,
                                     ).first()

    if ensemble:
        #add points for previous users
        for u in ensemble.users:
            for ea in u.ensemble_associations:
                # if the ensemble user A saved is the same one user B saved
                if ea.ensemble_id == ensemble.id:
                    ea.points += 1

        ensemble.users.append(user)
        db.session.add(ensemble)
        db.session.commit()
        print "added new User-Ensemble relationship"
    else:
        print "movie ID", movie_id
        print "dress ID", dress.id
        print "movie Name", Movie.query.filter(Movie.id == movie_id).first().name
        new_ensemble = Ensemble(accessory_id=accessory.id,
                            top_id=top.id,
                            bottom_id=bottom.id,
                            shoe_id=shoe.id,
                            bag_id=bag.id,
                            dress_id=dress.id,
                            movie_id=movie_id,
                            )

        new_ensemble.users.append(user)
        db.session.add(new_ensemble)
        db.session.commit()


    flash('Ensemble saved!')

    return redirect('/search')

def get_colors_from_movie(movie):
    """Get all colors from movies."""
    
    colors = Color.query.filter(Color.movie_id == movie.id).all()

    color_list = []

    for color in colors:
        color_list.append(color.hexcode)

    return color_list


@app.route('/shuffle_item')
def shuffle_item():
    """Shuffle individual category."""

    result = search_helper()

    # Get listing url of each category.
    top_listing = result[3]
    bottom_listing = result[4]
    accessory_listing = result[5]
    dress_listing = result[6]
    shoe_listing = result[7]
    bag_listing = result[8]

    # Get image url of each category.
    t_img_url = result[2]['top'][1]
    bo_img_url = result[2]['bottom'][1]
    a_img_url = result[2]['accessory'][1]
    b_img_url = result[2]['bag'][1]
    s_img_url = result[2]['shoe'][1]
    d_img_url = result[2]['dress'][1]

    #Colors
    colors = result[0]
    print "COLORS", colors
    top_color = colors[0]
    bottom_color = colors[1]
    accessory_color = colors[3]
    shoe_color = colors[2]
    dress_color = colors[0]
    bag_color = colors[4]

    # print "shuffle single top listing", t_img_url
    return jsonify(dict( top_color=top_color,
                        top_listing=top_listing,
                        t_img_url=t_img_url,
                        bottom_color=bottom_color,
                        bottom_listing=bottom_listing,
                        bo_img_url=bo_img_url,
                        accessory_color=accessory_color,
                        accessory_listing=accessory_listing,
                        a_img_url=a_img_url,
                        bag_color=bag_color,
                        bag_listing=bag_listing,
                        b_img_url=b_img_url,
                        dress_color=dress_color,
                        dress_listing=dress_listing,
                        d_img_url=d_img_url,
                        shoe_color=shoe_color,
                        shoe_listing=shoe_listing,
                        s_img_url=s_img_url))


def search_helper():
    """Search for list items matching with movie colors from Etsy."""

    if request.args.get("movie_name"):
        movie_name = request.args.get("movie_name")
        movie = Movie.query.filter(Movie.name == movie_name).one()
        session['movie'] = movie.name

    else:
        print 'RANDOMLY PICKING A MOVIE'
        movie = random.choice(Movie.query.all())

    color_list = get_colors_from_movie(movie)
    print 'Originally got colors %s from Movie %s' % (sorted(color_list), movie.name)

    result_dict = etsy.get_listing_items(color_list)

    print 'Colors returned       %s'  % (sorted(result_dict['colors']))
    
    best_dict = etsy.get_image_urls(result_dict, movie.id)
    
    (top_listing, bottom_listing, accessory_listing, dress_listing,
        shoe_listing, bag_listing) = etsy.get_listing_urls(best_dict)

    print 'returning ' , result_dict['colors']
    return (result_dict['colors'], movie, best_dict, top_listing, bottom_listing, accessory_listing, dress_listing,
        shoe_listing, bag_listing)


@app.route('/search_json')
def search_json():
    (colors, movie, best_dict, top_listing, bottom_listing, accessory_listing, dress_listing,
        shoe_listing, bag_listing) = search_helper()

    # return JSON
    return jsonify(dict(
            colors=colors,
            t_img_url=best_dict['top'][1],
            bo_img_url=best_dict['bottom'][1],
            s_img_url=best_dict['shoe'][1],
            a_img_url=best_dict['accessory'][1],
            b_img_url=best_dict['bag'][1],
            d_img_url=best_dict['dress'][1],
            top_listing=top_listing,
            bottom_listing=bottom_listing,
            accessory_listing=accessory_listing,
            shoe_listing=shoe_listing,
            bag_listing=bag_listing,
            dress_listing=dress_listing))


@app.route('/search')
def search():

    movie_list = Movie.query.all()

    color_dict = {}
    for movie in movie_list:
        color_dict[movie.name] = get_colors_from_movie(movie)

    movie_names = [m.name for m in movie_list]

    (colors, movie, best_dict, top_listing, bottom_listing, accessory_listing, dress_listing,
        shoe_listing, bag_listing) = search_helper()

    top_color = colors[4]
    print "TOP COLOR", top_color
    bottom_color = colors[1]
    print "BOTTOM COLOR", bottom_color
    dress_color = colors[0]
    print "DRESS COLOR", dress_color
    accessory_color = colors[2]
    print "ACCESSORY COLOR", accessory_color
    shoe_color = colors[3]
    print "SHOE COLOR", shoe_color
    bag_color = colors[4]
    print "BAG COLOR", bag_color

    print "COLORS", colors

    return render_template('search.html',
                                movie_list=movie_list,
                                color_dict=color_dict,
                                user_id=session.get('logged_in'),
                                logged_in=bool(session.get('logged_in')),
                                chosen_movie=session.get('movie'),
                                movie_names=movie_names,
                                t_img_url=best_dict['top'][1],
                                bo_img_url=best_dict['bottom'][1],
                                s_img_url=best_dict['shoe'][1],
                                a_img_url=best_dict['accessory'][1],
                                b_img_url=best_dict['bag'][1],
                                d_img_url=best_dict['dress'][1],
                                top_listing=top_listing,
                                bottom_listing=bottom_listing,
                                accessory_listing=accessory_listing,
                                shoe_listing=shoe_listing,
                                bag_listing=bag_listing,
                                dress_listing=dress_listing,
                                movie_id=movie.id,
                                top_color=top_color,
                                dress_color=dress_color,
                                bottom_color=bottom_color,
                                accessory_color=accessory_color,
                                shoe_color=shoe_color,
                                bag_color=bag_color
                            )

@app.route('/blacklist', methods=['POST'])
def blacklist():
    # get form url
    # update value to blacklisted
    # query db for cached table, key, listing id, compare w form url
    blacklisted = request.form.get('key')
    print blacklisted

    find_ld = re.search(r"listing/(\d+)/", blacklisted)

    listing_id = find_ld.groups()[0]

    blacklisted_url = "https://openapi.etsy.com/v2/listings/{}/images?api_key=w4kl15san4n93vl9sc0b01m8".format(listing_id)
    print "BLACKLISTED URL", blacklisted_url
    cached_result = Cache.query.filter(Cache.key == blacklisted_url).first()

    if not cached_result:
        print "couldn't be found"

        return None
    cached_result.blacklisted = True
    db.session.commit()

    return redirect('/search')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode


    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    
    app.run(port=5000, host='0.0.0.0')