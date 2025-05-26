from selenium import webdriver
import selenium
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
import keyboard
import undetected_chromedriver


def file_parsing(filee):
    type_of_cars=[]
    with open(filee, 'r') as file:
        type_of_carss = file.readlines()
    for i in range(0,len(type_of_carss),2):
        type_of_cars.append(type_of_carss[i].strip())
    return type_of_cars


def main(car_make):
    global driver

    all_cars_html = []
    for i in range(13,101):
        print(i)

        url = f"http://drive.com.au/cars-for-sale/search/used/all/all/{car_make}/page/{i}"
        driver.get(url)

        if outofrange() == True:
            print('breaking')
            break

        else:
            all_cars_html += get_page_of_cars() #these are upto 

    id_links = parse_id_links(all_cars_html)
    # print(id_links)
    info = parse_info(id_links)


def parse_id_links(all_cars_html):
    all_ids_links = []
    for j in all_cars_html:
        link = j.find('a', attrs={"data-cy": "CarThumbnail-permalink"})['href']
        x = link.split('car/')
        all_ids_links.append(str(x[-1][:-1]))
    return all_ids_links


def parse_info(id_links):
    global driver
    '''
    need to find:
    Vheicle
    Location
    km
    engine
    body type 
    Transmission
    Fuel type
    Fuel efficiency
    Registration number
    Colour
    VIN
    '''
    for Id in id_links:
        url = f"https://www.drive.com.au/cars-for-sale/car/{Id}/"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        print()
        
        print(url)

        vheicle = find_vheicle(soup)
        print(vheicle)

        price = find_price(soup)
        print(price)

        other_info = other_infomation(soup)

#apart of parse info
def find_vheicle(soup):
        vheicle = soup.find('div', class_="aside listing-left-aside single-listing_drive-listing__info-wrapper__fBl2H")
        vheicle = vheicle.find('h1', class_="carInfo_drive-cfs__car-info__listing-details__name___R2if").text
        return vheicle

#apart of parse info
def find_price(soup):

    #price
    try:
        price = soup.find('div',class_="priceInfoListing_drive-cfs__listing-info-price__wrapper__lJNH1")
        price = price.find('p',class_="priceInfoListing_drive-cfs__listing-info-price__original__value__gYdq7").text
    except:
        return "No price listed"
    return price




def other_infomation(soup):
    Normal_Or_NotNormal = None


    specs = soup.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__wrapper__RIIAm")
    all_specs = specs.findAll('li',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-item__fzCI1")

    for idx, k in enumerate(all_specs):
        idx = idx+1

        if idx == 1:
            Kilometers = k.find('div',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-details__6M8L2")
            Kilometers = Kilometers.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
            print(Kilometers)

        if idx == 2:
            Normal_Or_NotNormal = k.find('h4',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-heading__r9T0S").text

            if Normal_Or_NotNormal == "Engine":
                Normal_Or_NotNormal = True
            else:
                Normal_Or_NotNormal = False
        

        #When Normal:
        if Normal_Or_NotNormal == True:

            if idx == 2:
                Engine_type = k.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-details__uy5Jk")
                Engine_type = Engine_type.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Engine_type)

            elif idx == 4:
                Body_Type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Body_Type)

            elif idx == 5:
                Drive_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Drive_type)

            elif idx == 6:
                Fuel_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Fuel_type)

            elif idx == 7:
                Fuel_efficiency =k.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Fuel_efficiency)

            elif idx == 8:
                Transmission = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Transmission)



#FAAAAAAAAAALLLLLSEEE
        if Normal_Or_NotNormal == False:
            if idx == 3:
                print("Not normal not normal")
                Engine_type = k.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-details__uy5Jk")
                Engine_type = Engine_type.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Engine_type)
            
            elif idx == 5:
                Body_Type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Body_Type)

            elif idx == 6:
                Fuel_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Fuel_type)

            elif idx == 7:
                Transmission = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
                print(Transmission)

        else:
            pass







#not apart of parse info
def get_page_of_cars():
    global driver

    soup = BeautifulSoup(driver.page_source, "html.parser")

    a = soup.find('div', class_="search_drive-cfs__results__KaGCe")
    a = a.find('div', class_="listings_drive-cfs__listings__wrapper__HYl4u")

    all_cars_html = a.findAll('div', class_="listing-details-card_drive-marketplace__listing-card__oQwPi")


    return all_cars_html

def outofrange():
    global driver

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:

        finding_end = soup.find('div', class_="noResult_drive-no-results__6i5M_")
        finding_end = finding_end.find('p', class_="noResult_drive-no-results__content__En70T").text


    except:
        finding_end = None

    try:
        finding_start_error = soup.find('h4',class_="__404_drive-404__sub-text__qF0bu").text
    except:
        finding_start_error = None

    if finding_end != None or finding_start_error != None:
        print("stop going")
        return True
    print("keep going")
    return False

    

if __name__ == "__main__":
    filee = "all_cars.txt"
    driver = undetected_chromedriver.Chrome()

    for i in file_parsing(filee):
        main(i)
        break
print('quit')
driver.quit()
