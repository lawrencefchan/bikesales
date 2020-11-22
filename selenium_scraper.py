# %%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# import xlsxwriter
import datetime
import configparser
import os.path
import numpy
from collections import namedtuple
import matplotlib.pyplot as plt


def get_average(list):
    price_list = []
    for item in list:
        price = item[4]
        price_list.append(price)
    return numpy.average(price_list)


# driver = webdriver.Chrome('./chromedriver87.exe')
# driver.get("https://www.python.org")


firefox_profile = webdriver.FirefoxProfile()

firefox_profile.add_extension('quickjava.xpi')
firefox_profile.set_preference("thatoneguydotnet.QuickJava.curVersion", "2.1.0") ## Prevents loading the 'thank you for installing screen'
firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Images", 2)  ## Turns images off
firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.AnimatedImage", 2)  ## Turns animated images off
firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Flash", 2)  ## Flash
firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Java", 2)  ## Java
firefox_profile.set_preference("thatoneguydotnet.QuickJava.startupStatus.Silverlight", 2)  ## Silverlight


driver = webdriver.Firefox(firefox_profile)

transmission_switch = True
price_switch = True




# %%

# setup config file. if it exists, load it
config = configparser.ConfigParser()
if os.path.isfile('carsales_calc.ini'):
    config.read('carsales_calc.ini')
    user_settings = config["user"]
    user_state = user_settings["State"]
    if "Transmission" in user_settings:
        user_transmission = user_settings["Transmission"]
    else:
        transmission_switch = False
    if "Min price" in user_settings:
        price_min, price_max = user_settings["Min price"], user_settings["Max price"]
    else:
        price_switch = False
    kms_min, kms_max = user_settings["Min kms"], user_settings["Max kms"]
else:
    config.add_section("user")
    user_settings = config["user"]
    print("Enter your State")
    user_state = input("> ")
    user_settings["State"] = user_state
    print("Enter your Transmission")
    user_transmission = input("> ")
    if user_transmission == "":
        transmission_switch = False
    else:
        user_settings["Transmission"] = user_transmission
    print("Enter your price range separated by commas")
    user_price_range = input("> ")
    if user_price_range == "":
        price_switch = False
    else:
        price_min, price_max = user_price_range.replace(' ','').split(",")
        user_settings["Min price"] = price_min
        user_settings["Max price"] = price_max
    print("Enter your KM range separated by commas")
    user_kms_range = input("> ")
    kms_min, kms_max = user_kms_range.replace(' ','').split(",")
    user_settings["Min kms"] = kms_min
    user_settings["Max kms"] = kms_max
    print("Saving config file.")
    with open('carsales_calc.ini', 'w') as configfile:
        config.write(configfile)

if transmission_switch:
    transmission_string = "%26GenericGearType%3D%5B" + user_transmission + "%5D%29"
else:
    transmission_string = ""

if price_switch:
    price_string = "%26Price%3Drange%5B" + str(price_min) + ".." + str(price_max) + "%5D%29"
else:
    price_string = ""

print("Enter car make and model")
car_choice = input("> ")

user_make, user_model = car_choice.split(" ")

print("Searching Carsales")
driver.get("http://www.carsales.com.au/cars/results?q=%28%28%28%28%28%28%2"
            + "8Make%3D%5B" + user_make
            + "%5D%26Model%3D%5B" + user_model
            + "%5D%29%26State%3D%5B" + user_state
            + "%5D%29%26Service%3D%5BCarsales%5D%29"
            + transmission_string
            + price_string
            + "%26Odometer%3Drange%5B"
            + str(kms_min) + ".." + str(kms_max)
            + "%5D%29%26%28BodyStyle%3D%5BHatch%5D%7CBodyStyle"
            + "%3D%5BSedan%5D%29%29&sortby=Year&limit=24")

num_search_results = int(driver.find_elements_by_css_selector("div.results-title")[0].text.split(' ')[0])

if num_search_results > 24:
    pagination_div = driver.find_elements_by_css_selector("div.pagination")[0]
    page_count = int(pagination_div.find_elements_by_tag_name("p")[0].text.split(' ')[1])
    next_page_link = pagination_div.find_elements_by_partial_link_text("Next")[0].get_attribute('href')
else:
    page_count = 1
current_page = 1
car_list = []
tuple_list = []
Car = namedtuple("Car", ['link', 'title', 'year', 'kms', 'price'])

while current_page <= page_count:
    print("Loading page", str(current_page))
    page_listings = driver.find_elements_by_css_selector("div.listing-item")
    real_page_listings = []
    for car in page_listings:
        if not "contentcards" in car.get_attribute('class') and not "gcad" in car.get_attribute('class'):
            real_page_listings.append(car)
    for car in real_page_listings:
        car_link = car.find_elements_by_tag_name('a')[0].get_attribute('href')
        car_title = car.find_elements_by_tag_name('h2')[0].text
        print("Adding", car_title)
        car_year = int(car_title.split(' ')[0])
        car_price = int(car.find_elements_by_css_selector('div.price')[0].text.strip("$*").replace(",",""))
        car_kms = int(car.find_elements_by_css_selector('div.feature-text')[0].text.strip(" km").replace(",",""))
        car_tuple = Car(car_link, car_title, car_year, car_kms, car_price)
        tuple_list.append(car_tuple)
        car_list.append({
            'year': car_year,
            'kms': car_kms,
            'price': car_price,
            })
    if current_page < page_count:
        pagination_div = driver.find_elements_by_css_selector("div.pagination")[0]
        next_page_link = pagination_div.find_elements_by_partial_link_text("Next")[0].get_attribute('href')
        driver.get(next_page_link)
    current_page += 1

N = 50
x = [x['year'] for x in car_list]
# x_axis.count(year)
y = [x['price'] for x in car_list]
area = numpy.pi * (5 * numpy.random.rand(N))**2

plt.scatter(x, y, s=area)
z = numpy.polyfit(x, y, 1)
p = numpy.poly1d(z)

plt.plot(x,p(x),"r--")

plt.show()
# by_year = []
# years_done = []
# for car in car_list:
#     year_list = []
#     for sublist in car_list:
#         if car[2] == sublist[2]:
#             year_list.append(sublist)
#     if not car[2] in years_done:
#         by_year.append(year_list)
#         years_done.append(car[2])
#
# # link, title, year, kms, price
# now = datetime.datetime.now()
# now_string = now.strftime("%d-%m-%y %H.%M")
# workbook_filename = user_make + ' ' + user_model + ' ' + now_string + '.xlsx'
# print("Creating spreadsheet", workbook_filename)
# workbook = xlsxwriter.Workbook(workbook_filename)
# worksheet = workbook.add_worksheet()
#
# bold = workbook.add_format({'bold': 1})
# url_format = workbook.add_format({'font_color': 'blue','underline': 1})
#
# worksheet.write('A1', 'Link', bold)
# worksheet.write('B1', 'Year', bold)
# worksheet.write('C1', 'Kilometres', bold)
# worksheet.write('D1', 'Price', bold)
#
# row = 1
# col = 0
#
# for car in car_list:
#     row = car_list.index(car) + 1
#     worksheet.write_url(row, col, car.link, url_format, car.title)
#     worksheet.write_number(row, col + 1, car.year)
#     worksheet.write_number(row, col + 2, car.kms)
#     worksheet.write_number(row, col + 3, car.price)
#
#
# worksheet2 = workbook.add_worksheet()
#
# worksheet2.write('A1', 'Year', bold)
# worksheet2.write('B1', 'Average', bold)
# worksheet2.write('C1', 'Count', bold)
#
# row = 1
# col = 0
#
# for year in by_year:
#     row = by_year.index(year) + 1
#     average = get_average(year)
#     car_num = len(year)
#     worksheet2.write_number(row, col, year[0][2])
#     worksheet2.write_number(row, col + 1, average)
#     worksheet2.write_number(row, col + 2, car_num)
#
#
#
# print("Saving spreadsheet")
# workbook.close()
