'''
    This project is a simple learning exercise for getting into web scraping.

    For this I will be using the libraries "lxml" and "requests"

'''

from lxml import html

import requests

#Specifying global default search type
SEARCH_BD_MV_TYPE = "Popularity"

#Title search URL https://www.mightyape.co.nz/movies-tv/movies/all?sort=2&q=movieformat~blu-ray

#First function grabes results from the first website

Default_Location = "private_data/"
Default_File = "private_link.txt"

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
            temp_mv = Movie_object(title,format[0],rating[0].strip(), mape_main_url + link,normal_price, base_price, hot_price)
            mape_list[title] = temp_mv
        else :
            temp_mv = Movie_object(title, format[0], 'n/a', mape_main_url + link, normal_price, base_price, hot_price)
            mape_list[title] = temp_mv


        count += 1

    return mape_list

class Movie_object(object):
    def __init__(self,title, format,rating,link,nprice,price,hprice):
        self.title = title
        self.format = format
        self.rating = rating
        self.link = link
        self.price = price
        self.nprice = nprice
        self.hprice = hprice
    def get_format (self):
        return self.format
    def get_rating (self):
        return self.rating
    def get_link (self):
        return self.link
    def get_prices(self):
        return self.price,'|', self.hprice
    def get_nprice(self):
        return self.nprice
    def get_price(self):
        return self.price
    def get_hprice(self):
        return self.hprice
    def __str__(self):
        return '%s | %s | %s \tLink: %s\n\t @ normal: %s | new: %s | Special: %s'%(self.title,self.format,self.rating,self.link,self.price, self.nprice, self.hprice)

    '''def __repr__(self):
        return self.title, '|', self.format, '|', self.rating,'\tLink:', self.link,'@',self.price, '|', 'Special:', self.hprice
    The below loop works! Do not touch'''

def private_link_loader():
    with open(Default_Location + Default_File, 'r') as f:
        private_link = f.readline()
        link_string = private_link.split('=')[1].replace("'", "").strip()
        f.close()
    return link_string

"""copy_of_list = grab_mApe_results(search_by_Title)
for item in copy_of_list:
    print('',copy_of_list[item])"""


