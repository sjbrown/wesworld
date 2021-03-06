from random import shuffle

from random import choice

from sqlalchemy import desc

import requests

import json

import re

from flask import Flask

from model import User, Movie, Color, Ensemble, Cache, connect_to_db, db

import os
# print sorted(os.environ.keys())
etsy_api_key = os.environ["API_KEY"]

app = Flask(__name__)

DEBUG = False


class BlacklistedException(Exception):
    pass


def get_from_cache(key):
    '''

    '''
    if DEBUG:
        if 'listings/active' in key:
            return '''
            {
              "count": 40, 
              "type": "Listing", 
              "pagination": {
                "effective_limit": 10, 
                "effective_page": 1, 
                "next_page": 2, 
                "effective_offset": 0, 
                "next_offset": 10
              }, 
              "params": {
                "category": "clothing/shirt", 
                "min_price": null, 
                "lat": null, 
                "translate_keywords": "false", 
                "accepts_gift_cards": "false", 
                "tags": null, 
                "color": "5B1A18", 
                "region": null, 
                "sort_on": "score", 
                "lon": null, 
                "max_price": null, 
                "color_accuracy": "10", 
                "sort_order": "down", 
                "limit": "10", 
                "location": null, 
                "offset": 0, 
                "keywords": null, 
                "page": null, 
                "geo_level": "city"
              }, 
              "results": [
                {
                  "num_favorers": 7, 
                  "creation_tsz": 1492661415, 
                  "taxonomy_id": 482, 
                  "style": null, 
                  "item_length": "13", 
                  "has_variations": true, 
                  "original_creation_tsz": 1448168571, 
                  "shop_section_id": 16456044, 
                  "used_manufacturer": false, 
                  "listing_id": 257398834, 
                  "user_id": 52137148, 
                  "processing_min": 3, 
                  "title": "Firefighter Dad T-shirt", 
                  "processing_max": 5, 
                  "taxonomy_path": [
                    "Clothing", 
                    "Unisex Adult Clothing", 
                    "Tops & Tees", 
                    "T-shirts"
                  ], 
                  "views": 84, 
                  "last_modified_tsz": 1492661415, 
                  "state": "active", 
                  "is_digital": false, 
                  "shipping_template_id": 19480236723, 
                  "is_customizable": true, 
                  "item_height": "2", 
                  "state_tsz": 1475804494, 
                  "description": "foo", 
                  "tags": [
                    "firefighter", 
                    "daughter", 
                    "fire", 
                    "Tshirt", 
                    "shirt", 
                    "custom", 
                    "personalized", 
                    "hero", 
                    "D", 
                    "Dad"
                  ], 
                  "price": "17.50", 
                  "item_weight": "12", 
                  "item_width": "10", 
                  "who_made": "i_did", 
                  "category_path_ids": [
                    69150353, 
                    68889876
                  ], 
                  "file_data": "", 
                  "recipient": "unisex_adults", 
                  "is_private": false, 
                  "category_path": [
                    "Clothing", 
                    "Shirt"
                  ], 
                  "non_taxable": false, 
                  "ending_tsz": 1503202215, 
                  "is_supply": "false", 
                  "language": "en-US", 
                  "url": "https://www.etsy.com/listing/257398834/firefighter-dad-t-shirt?utm_source=wesworld&utm_medium=api&utm_campaign=api", 
                  "when_made": "made_to_order", 
                  "materials": [], 
                  "item_dimensions_unit": "in", 
                  "currency_code": "USD", 
                  "occasion": null, 
                  "category_id": 68889876, 
                  "item_weight_units": null, 
                  "featured_rank": null, 
                  "quantity": 64
                }
              ]
            }

            '''
        elif '/images' in key:
            return '''
                {
                  "count": 1, 
                  "type": "ListingImage", 
                  "pagination": {}, 
                  "params": {
                    "listing_id": "512396261"
                  }, 
                  "results": [
                    {
                      "blue": 29, 
                      "hue": 30, 
                      "saturation": 74, 
                      "full_width": 640, 
                      "creation_tsz": 1487174941, 
                      "brightness": 43, 
                      "url_75x75": "https://img0.etsystatic.com/142/0/14632618/il_75x75.1143639922_ep7m.jpg", 
                      "full_height": 640, 
                      "listing_id": 512396261, 
                      "rank": 1, 
                      "hex_code": "70471D", 
                      "green": 71, 
                      "listing_image_id": 1143639922, 
                      "url_170x135": "https://img0.etsystatic.com/142/0/14632618/il_170x135.1143639922_ep7m.jpg", 
                      "is_black_and_white": false, 
                      "url_570xN": "https://img0.etsystatic.com/142/0/14632618/il_570xN.1143639922_ep7m.jpg", 
                      "red": 112, 
                      "url_fullxfull": "https://img0.etsystatic.com/142/0/14632618/il_fullxfull.1143639922_ep7m.jpg"
                    }
                  ]
                }

            '''


    cache_result = Cache.query.filter(Cache.key == key).first()
    if cache_result is None:
        return None
    if cache_result.blacklisted is True:
        print "BLACKLISTED EXCEPTION"
        raise BlacklistedException()
    return cache_result.value


def cache(key, value):
    """Instantiating new cached results."""
    new_cache_result = Cache(key=key, value=value)
    db.session.add(new_cache_result)
    db.session.commit()


def cached_get(url, force_no_blacklist=False):
    """Get cached results."""

    try:
        value = get_from_cache(url)
    except BlacklistedException:
        if force_no_blacklist:
            print "FORCING NO BLACKLIST", url
            return (
                json.loads('''{
                  "count": 1, 
                  "type": "ListingImage", 
                  "pagination": {}, 
                  "params": {
                    "listing_id": "512396261"
                  }, 
                  "results": [
                    {
                      "full_width": 640,
                      "full_height": 640, 
                      "listing_id": 512396261,
                      "listing_image_id": 1143639922,
                      "url_570xN": "/static/css/images/profile_pic/m_8.jpg"
                    },
                    {
                      "full_width": 640, 
                      "full_height": 640, 
                      "listing_id": 512396261, 
                      "hex_code": "70471D", 
                      "listing_image_id": 1143639922,
                      "url_570xN": "/static/css/images/profile_pic/m_8.jpg"
                    }
                  ]
                }

            ''')
                , 200
              )
        else:
            print "BLACKLISTED URL", url
            return None, 400
    
    if value:
        return json.loads(value), 200

    response = requests.get(url)

    if response.status_code != 200:
        return None, response.status_code
        
    response_json = response.json() 
    cache(url, response.text)
    return response_json, response.status_code


def get_results(color, etsy_category, accuracy=10):
    """Get results either from cached records or live queries."""
    
    # Create template url for all list item urls.
    item_url_template = (
        'https://openapi.etsy.com/v2/listings/active?color={}&color_accuracy=' +
        str(accuracy) +
        '&limit=20&sort_on=score&category={}&api_key=' +
        etsy_api_key
    )

    url = item_url_template.format(color, etsy_category)
    # print 'Requesting', url
    j, status_code = cached_get(url)
    if status_code != 200:
        print 'Problem fetching', url
        return []
    if 'results' not in j or len(j['results']) == 0:
        print 'Problem - no results in ', url
        if accuracy >= 30:
            return []
        return get_results(color, etsy_category, accuracy + 20)
    return j['results']


def get_listing_items(color_list):
    """Getting search results from Wes Anderson color palettes."""

    # Shuffle the color list.
    shuffle(color_list)
    print "color list", color_list

    # Get the first five items outof the shuffled color list.
    top_color, bottom_color, shoe_color, accessory_color, bag_color = color_list[:5]

    # Getting dict results from Etsy urls.
    return dict(
        colors=[top_color, bottom_color, shoe_color, accessory_color, bag_color],

        # top color results
        shirt_results=get_results(top_color, "clothing/shirt"),
        jacket_results=get_results(top_color, "clothing/jacket"),
        sweatshirt_results=get_results(top_color, "clothing/sweatshirt"),
        tank_results=get_results(top_color, "clothing/tank"),
        dress_results=get_results(top_color, "clothing/dress"),

        # bottom color results
        pants_results=get_results(bottom_color, "clothing/pants"),
        skirt_results=get_results(bottom_color, "clothing/skirt"),
        shorts_results=get_results(bottom_color, "clothing/shorts"),

        # shoe color results
        shoe_results=get_results(shoe_color, "clothing/shoes"),
        socks_results=get_results(shoe_color, "clothing/socks"),

        # accessory color results
        accessory_results=get_results(accessory_color, "accessories"),
        jewelry_results=get_results(accessory_color, "jewelry"),

        # bag color results
        bag_results=get_results(bag_color, "bags_and_purses"),
    )


def get_search_results(result_dict):
    """Create search results by categories."""
    
    accessory_results = (result_dict['accessory_results'][:10] 
                        + result_dict['jewelry_results'][:20])

    shuffle(accessory_results)

    bag_results = result_dict['bag_results'][:20]
    shuffle(bag_results)

    dress_results = result_dict['dress_results'][:20]
    shuffle(dress_results)

    bottom_results = (result_dict['pants_results'][:6] + 
                      result_dict['skirt_results'][:6] + 
                      result_dict['shorts_results'][:6])
    shuffle(bottom_results)


    top_results = (result_dict['shirt_results'][:5] +
                   result_dict['sweatshirt_results'][:5] +
                   result_dict['tank_results'][:5] +
                   result_dict['jacket_results'][:10])

    shuffle(top_results)

        
    shoe_results = (result_dict['shoe_results'][:15] +
                    result_dict['socks_results'][:10]
                    )
    shuffle(shoe_results)

    return (accessory_results,
            bag_results,
            dress_results,
            bottom_results,
            top_results,
            shoe_results)


def get_best_result(results, color=None, force_no_blacklist=False):
    """
    Ruling out irrelevant listing images.
    Input:
     - results is a list of dicts.   Each dict must have key 'listing_id'
    """

    for result in results:
        # print "inside for loop\n"
        listing_id = result["listing_id"]
        image_url_template = "https://openapi.etsy.com/v2/listings/{}/images?api_key=" + etsy_api_key
        url = image_url_template.format(listing_id)
        url_dict, status_code = cached_get(url, force_no_blacklist)
        
        # TODO Handle status code != 200
        if status_code != 200:
             continue

        num_imgs = len(url_dict['results'])

        if num_imgs > 1 and len(url_dict['results'][0]) > 0:

            print 'type for urldict-results', type(url_dict['results'])
            print 'result 0', str(url_dict['results'][0])[:50]

            return result, url_dict['results'][0]["url_570xN"] # TypeError: list indices must be integers, not str
        else:
            print "rejecting bad images.", url

    return None, None


def fix_missing_listings(url_type, results, movie_id):
    """Helper function to replenish missing results via Etsy API calls with
    db records.
    """
    if results:
        result, img_url = get_best_result(results)
        if result is not None:
            return result, img_url

    print 'grabbing the first one from the db'
    '''
    query the ensemble table for Ensemble.movie_id == movie_id
    return the dress url
    put it into dress_results
    call get_best_result(dress_results)
    '''
    ensemble = Ensemble.query.filter(Ensemble.movie_id == movie_id).first()

    url = ''
    if (url_type == 'accessory_url'):
        url = ensemble.accessory.listing_url
        print "accessory URL", url
    elif (url_type == 'top_url'):
        url = ensemble.top.listing_url
    elif (url_type == 'bottom_url'):
        url = ensemble.bottom.listing_url
    elif (url_type == 'shoe_url'):
        url = ensemble.shoe.listing_url
    elif (url_type == 'bag_url'):
        url = ensemble.bag.listing_url
    elif (url_type == 'dress_url'):
        url = ensemble.dress.listing_url

    m = re.search(r"listing/(\d+)/", url)
    print "fixing url type", url_type, url
    
    listing_id = m.groups()[0]

    listing_dict = {
        'listing_id': listing_id,
        'url': url,
    }

    result, img_url = get_best_result([listing_dict], force_no_blacklist=True)

    return result, img_url


def get_image_urls(result_dict, movie_id):
    """Creating image urls for the ensemble."""
    
    try:
        (accessory_results,
            bag_results,
            dress_results,
            bottom_results,
            top_results,
            shoe_results) = get_search_results(result_dict)

        best_results_and_img_urls = {}

        a_result, a_img_url = fix_missing_listings('accessory_url', accessory_results, movie_id)
        best_results_and_img_urls['accessory'] = (a_result, a_img_url)
        
        d_result, d_img_url = fix_missing_listings('dress_url', dress_results, movie_id)
        #print "dress result, dress image", (d_result, d_img_url)
        best_results_and_img_urls['dress'] = (d_result, d_img_url)

        t_result, t_img_url = fix_missing_listings('top_url', top_results, movie_id)
        best_results_and_img_urls['top'] = (t_result, t_img_url)

        bo_result, bo_img_url = fix_missing_listings('bottom_url', bottom_results, movie_id)
        best_results_and_img_urls['bottom'] = (bo_result, bo_img_url)

        b_result, b_img_url = fix_missing_listings('bag_url', bag_results, movie_id)
        best_results_and_img_urls['bag'] = (b_result, b_img_url)

        s_result, s_img_url = fix_missing_listings('shoe_url', shoe_results, movie_id)
        best_results_and_img_urls['shoe'] = (s_result, s_img_url)


    except IndexError as e:
        print e
        
    return best_results_and_img_urls


def get_listing_urls(best_dict):
    """Get listing urls."""

    # print "best dict keys", best_dict.keys()
    best_top = best_dict['top'][0]
    best_bottom = best_dict['bottom'][0]
    best_accessory = best_dict['accessory'][0]
    best_shoe = best_dict['shoe'][0]
    best_dress = best_dict['dress'][0]
    best_bag = best_dict['bag'][0]

    dress_listing = best_dress["url"]

    print "dress url", dress_listing
 
    top_listing = best_top["url"]
    # print "top url", top_listing

    bottom_listing = best_bottom["url"]
    # print "bottom url", bottom_listing
    
    shoe_listing = best_shoe["url"]
    # print "shoe url", shoe_listing

    accessory_listing = best_accessory["url"]
    # print "accessory url", accessory_listing

    bag_listing = best_bag["url"]
    # print "bag url", bag_listing

    return (top_listing, bottom_listing, accessory_listing, 
            dress_listing, shoe_listing, bag_listing)


if __name__ == '__main__':

    def close():
        db.session.close()
        #db.dispose()

    connect_to_db(app)

    result_dict = get_listing_items(["F1BB7B", "FD6467", "5B1A18", 
        "D67236", "E6A0C4", "C93312", "FAEFD1", "DC863B", "798E87", "C27D38", "CCC591"])

    x = get_image_urls(result_dict, 5)

    y = get_listing_urls(x)

