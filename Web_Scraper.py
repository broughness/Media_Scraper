'''
    This project is a simple learning exercise for getting into web scraping.

    For this I will be using the libraries "lxml" and "requests"

'''

from lxml import html
from urllib import parse
import json

import requests

#Specifying global default search type
SEARCH_BD_MV_TYPE = "Popularity"

#Title search URL https://www.mightyape.co.nz/movies-tv/movies/all?sort=2&q=movieformat~blu-ray

#First function grabes results from the first website

Default_Location = "private_data/"
Default_File = "private_link.txt"
Default_OMDb_api_key = "private_key.txt"

def private_link_loader():
    with open(Default_Location + Default_File, 'r') as f:
        private_link = f.readline()
        link_string = private_link.split('=')[1].replace("'", "").strip()
        f.close()
    return link_string

def laod_api_key ():
    with open(Default_Location + Default_OMDb_api_key, 'r') as f:
        api_key_raw = f.readline()
        key = api_key_raw.split(':')[1].strip()
        f.close()
    return key

def imdb_search( title ):
    if title is not None:
        #http://www.omdbapi.com/?i=[ttnumber]&apikey=
        #http://www.omdbapi.com/?t=[title]&apikey=
        url_pre = "http://www.omdbapi.com/?t="
        url_post = "&apikey="
        encoded_title = parse.quote_plus(title)
        full_url = url_pre+encoded_title+url_post+laod_api_key()
        results = requests.get(full_url)
        if results.status_code is 200:
            return results.content
        else :
            raise IOError("Bad return code: "+results.status_code)

def pars_imdb_object( data ):
    #Remove starting "b'{" and ending "}" characters.
    json_data = data.decode('utf8')
    #clean_data = str(data)[3:-2:1]
    print(json_data)
    return(json_data)

def laod_imdb_object( jasonData ):
    #basic: [title, imdbID, format]
    data_copy = json.loads(jasonData)
    #data_test = json.load(data_copy)
    print(data_copy)
    if "title" and "imdbID" and "DVD" in data_copy:
        title = data_copy['Title']
        imdbId = data_copy['imdbID']
        format = "blu-ray"
        dvd_released = data_copy['DVD']
        newObject = Movie_object(title,imdbId,format)
    return newObject


def grab_mApe_wishList(id_string) :

    returned_data = ""
    mape_wishList_url = 'https://www.mightyape.co.nz/wishlist/'+id_string
    print("Grabbing results from:",mape_wishList_url)
    page = requests.get(mape_wishList_url)
    print("Status:",page.status_code)
    #print(page.content)
    tree = html.fromstring(page.content)

    products = tree.xpath('//div[@class="product wishlist-item"]')  # <--- WORKS

    lineNum = 1
    for product in products:
        base_xpath = product.xpath('div[@class="detail"]/a')
        alt_text = base_xpath[0].text+" "
        url = product.xpath('div[@class="detail"]/a/@href')[0]+" "
        title = product.xpath('div[@class="detail"]/a')[0].text+" "
        format = product.xpath('div[@class="detail"]/div[@class="format"]')[0].text + " "
        image_url_sml = product.xpath('div[@class="item"]/div[@class="image"]/a/img/@src')
        #print("[Image url]",image_url_sml,format)
        #image_url_lrg = product.xpath('div[@class="detail"]/a/@href')[0] + " "

        current_price = product.xpath('div[@class="pricing"]/div[@class="product-price"]/span')[0].text+" "
        previous_price = product.xpath('div[@class="pricing"]/div[@class="saving"]/s')
        if len(previous_price) > 0 :
            formatted_prev_price = float(str(previous_price[0].text).replace("$",""))
            price_difference = formatted_prev_price - float(str(current_price).replace("$",""))
            percent_off = price_difference/formatted_prev_price * 100
            formatted_price_difference = str(round(price_difference,2))+" "
            formatted_percent_off = str(round(percent_off,2))+"%"
            this_line = str('<p id="line'+str(lineNum)+'" class="output-data"> ') + str(title)+str(url)+str(alt_text)+"~ On sale "+str(current_price)+"reduced from $"+str(formatted_prev_price)+" saving of $"+str(formatted_price_difference)+str(formatted_percent_off)+" off </p>"
            #print(title, url, alt_text,"~ On sale", current_price,"reduced from "+previous_price[0].text, "saving of $"+str(formatted_price_difference),str(formatted_percent_off)+" off")
            print(this_line)
            returned_data = returned_data + this_line
        else :
            this_line = str('<p id="line'+str(lineNum)+'" class="output-data"> ') + str(title)+str(url)+str(alt_text)+str(current_price)+"Normal Price </p>"
            #print(title, url, alt_text, current_price, "Normal Price")
            print(this_line)
            returned_data = returned_data + this_line
        lineNum += 1

    return returned_data

"""
    Future function to output to text file.
    - Not yet implemented!
"""
def output_to_html(string_data):
    raise NotImplementedError("This function is not yet Implemented!")


def search_mApe_title (title,format):
    #https://www.mightyape.co.nz/movies-tv/movies/all?q=ant+man+movieformat~blu-ray
    """
                This Function takes as input a title and format type to search by
                and returns a list of results.
             :param title: Title of movie to search
             :param format: Format of media to search
             :return: MightyApe results from website
        """

    mape_main_url = 'https://www.mightyape.co.nz/'
    # Defining the url paths for search types
    mape_mv_category_url = 'movies-tv/movies/all?q='+parse.quote_plus(title)+"+"
    mape_mv_format_search_url = 'movieformat~'+format

    # This is the final url string

    searchUrl = mape_main_url+mape_mv_category_url+mape_mv_format_search_url
    #'https://www.mightyape.co.nz/movies-tv/movies/all?sort=2&q=movieformat~blu-ray'

    # Using a dictionary to store data, as contains list with objects
    mape_list = {}

    page = requests.get(searchUrl)
    tree = html.fromstring(page.content)

    data = tree.xpath(
        '//div[@class="product-list gallery-view"]/div[@class="product"]/div[@class="title"]/a')  # <--- WORKS

    data_alt = tree.xpath('//div[@class="product-list gallery-view"]/div[@class="product"]')

    print('Getting results from url:', searchUrl)
    print('Number of objects=', len(data_alt))
    count = 1

    for item in data_alt:
        simple_item = item.xpath('div[@class="title"]/a')
        title = simple_item[0].text
        link = simple_item[0].get('href')
        format = item.xpath('div[@class="format"]/text()')
        rating = item.xpath('div[@class="customer-rating"]/span/span[@class="average"]/text()')
        base_price = item.xpath('div[@class="price"]/s/text()')
        hot_price = item.xpath('div[@class="price"]/span[@class="price hot"]/text()')
        normal_price = item.xpath('div[@class="price"]/span[@class="price"]/text()')
        if len(rating) > 0:
            # temp_mv = Movie_object(title,format[0],rating[0].strip(), mape_main_url + link,normal_price, base_price, hot_price)
            print(title, format[0], rating[0].strip(), mape_main_url + link, normal_price, base_price, hot_price)
            # mape_list[title] = temp_mv
        else:
            print(title, format[0], 'n/a', mape_main_url + link, normal_price, base_price, hot_price)
            # temp_mv = Movie_object(title, format[0], 'n/a', mape_main_url + link, normal_price, base_price, hot_price)
            # mape_list[title] = temp_mv

        count += 1

    return mape_list

def grab_mApe_results (searchType) :
    """
            This Function takes as input a type to search by
            and returns a list of results.
         :param searchType: Type of search to grab results from
         :return: MightyApe results from website
    """

    mape_main_url = 'https://www.mightyape.co.nz/'
    #Defining the url paths for search types
    mape_mv_category_url = 'movies-tv/movies?q='
    mape_mv_format_search_url = 'movieformat~blu-ray'

    #This is the final url string
    searchUrl = ''

    #Checking search type
    if searchType is SEARCH_BD_MV_TYPE :
        searchUrl = mape_main_url+mape_mv_category_url+mape_mv_format_search_url
    elif searchType is 'Title' :
        searchUrl = 'https://www.mightyape.co.nz/movies-tv/movies/all?sort=2&q=movieformat~blu-ray'


    #Using a dictionary to store data, as contains list with objects
    mape_list = {}

    page = requests.get(searchUrl)
    tree = html.fromstring(page.content)

    data = tree.xpath('//div[@class="product-list gallery-view"]/div[@class="product"]/div[@class="title"]/a') #<--- WORKS

    data_alt = tree.xpath('//div[@class="product-list gallery-view"]/div[@class="product"]')

    print('Getting results from url:',searchUrl)
    print('Number of objects=',len(data_alt))
    count = 1

    for item in data_alt :
        simple_item = item.xpath('div[@class="title"]/a')
        title = simple_item[0].text
        link = simple_item[0].get('href')
        format = item.xpath('div[@class="format"]/text()')
        rating = item.xpath('div[@class="customer-rating"]/span/span[@class="average"]/text()')
        base_price = item.xpath('div[@class="price"]/s/text()')
        hot_price = item.xpath('div[@class="price"]/span[@class="price hot"]/text()')
        normal_price = item.xpath('div[@class="price"]/span[@class="price"]/text()')
        if len(rating) > 0 :
            #temp_mv = Movie_object(title,format[0],rating[0].strip(), mape_main_url + link,normal_price, base_price, hot_price)
            print(title,format[0],rating[0].strip(), mape_main_url + link,normal_price, base_price, hot_price)
            #mape_list[title] = temp_mv
        else :
            print(title, format[0], 'n/a', mape_main_url + link, normal_price, base_price, hot_price)
            #temp_mv = Movie_object(title, format[0], 'n/a', mape_main_url + link, normal_price, base_price, hot_price)
            #mape_list[title] = temp_mv


        count += 1

    return mape_list

class Movie_object(object):
    def __init__(self,title, imdb, format):
        self.title = title
        self.imdbID = imdb
        self.format = format

        #Ratings format: { site: rating,}
        self.ratings = {}

        #Links format: { store: link, }
        self.links = {}

        #Prices format: { store: price, }
        self.prices = {}


    def get_title(self):
        return self.title

    def get_imdbID(self):
        return self.imdbID

    def get_format(self):
        return self.format



    def add_store (self, store, link, price):
        if store not in self.links :
            self.links[store] = link
            self.prices[store] = price

    def add_rating ( site, rating ):
        pass

    def get_format (self):
        return self.format
    def get_rating (self):
        return self.ratings
    def get_link (self):
        return self.links
    def get_prices(self):
        return self.prices

    def __str__(self):
        return "Title: %s \nimdb: %s \nFormat: %s"%(self.get_title(),self.get_imdbID(),self.get_format())

    """def __str__(self):
        return '%s | %s | %s \tLink: %s\n\t @ prices: %s'%(self.title,self.format,self.ratings,self.links,self.prices)"""

    '''def __repr__(self):
        return self.title, '|', self.format, '|', self.rating,'\tLink:', self.link,'@',self.price, '|', 'Special:', self.hprice
    The below loop works! Do not touch'''

"""copy_of_list = grab_mApe_results(search_by_Title)
for item in copy_of_list:
    print('',copy_of_list[item])"""


