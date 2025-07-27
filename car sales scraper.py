from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd


def list_car_brands(filee):
    type_of_cars=[]
    with open(filee, 'r') as file:
        type_of_carss = file.readlines()
    for i in range(0,len(type_of_carss),2):
        type_of_cars.append(type_of_carss[i].strip())
    return type_of_cars

def main(car_make):
    global driver

    all_cars_html = []

    for i in range(1,101):
        # STEP 1... ok so balsically this is step 1. Car brand goes in to this fucntion.
        print(i)

        url = f"http://drive.com.au/cars-for-sale/search/used/all/all/{car_make}/page/{i}"
        driver.get(url)

        
        if outofrange() == True:
            print('breaking')
            break
        else:
            all_cars_html += get_page_of_cars() #essentially this gets the htm in a list of all the cars on the page. in the loop 

    #LIST OF ALL CAR IDS...
    id_links = parse_id_links(all_cars_html)# ok so bascially this is a list of numbers for all car ids to put into the url.


    info = parse_info(id_links,car_make)#gets all infomation on cars...
    
    return info
    # print(info)
    '''
    [ 
    
    {brand 1 : [{"car1: ": car}, {'year: ': year}, {'price: ':price}]........ [{'car2: ' : car}]     },
    {brand 2 : ...                                                                                   },
    
    ]
    '''


# just the list of nubers of car ids
def parse_id_links(all_cars_html):
    all_ids_links = []
    for j in all_cars_html:
        link = j.find('a', attrs={"data-cy": "CarThumbnail-permalink"})['href']
        x = link.split('car/')
        all_ids_links.append(str(x[-1][:-1]))
    return all_ids_links


def parse_info(id_links,brand):
    global driver
    all_cars_data = []

    for Id in id_links:#id links looks at each individual car via ID.

        #now on specific webpage of just the car.
        url = f"https://www.drive.com.au/cars-for-sale/car/{Id}/"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        location = soup.findAll('a',class_="breadcrumbs_drive-breadcrumbs__back__6926m")
        location = location[3].text.strip()
        vheicle = find_vheicle(soup)
        price = find_price(soup)

        other_info = other_infomation(soup) # lists inside of it [[all info, 6, or 7], True or False]
        
        print(f"https://www.drive.com.au/cars-for-sale/car/{Id}/")
        print(vheicle)
        print(location)
        print()
        print(price)
        print()
        print(other_info)
        print("\n\n")
        
        if other_info[1]:  #THIS IS NORMAL when other_info[1] == True in other words
            year = find_year(soup)
            year_or_warranty = year

        else:  #THIS IS NOT NORMALLL
            warranty = warranty_check(soup)
            year_or_warranty = warranty

        car_data = parse_parse_info(url, vheicle, price, year_or_warranty, other_info,brand)
        all_cars_data.append(car_data)
    return all_cars_data

def parse_parse_info(url, vheicle, price, year_or_warrenty, other_info1, brand):
    all_car_details = {}
    all_car_details['car'] = vheicle
    all_car_details['price'] = price
    
    if other_info1[1] == True:#THIS IS WHEN NORMAL
        all_car_details['year'] = year_or_warrenty
        all_car_details['warranty'] = False
    else:#THIS IS NOT NORMAL
        all_car_details['warranty'] = year_or_warrenty
        try:
            all_car_details['year'] = int(vheicle.split()[0])
        except:
            all_car_details['year'] = "Year Not Found"
    

    for j in other_info1[0]:
        if j is None:
            continue
        try:
            words_tag = j[0].replace(':', '').strip().lower().replace(' ', '_')
            aa = j[1]
            if aa is not None:
                all_car_details[words_tag] = aa
        except (TypeError, IndexError) as e:
            print(f"Error processing attribute: {j}, error: {e}")
    return {brand: [all_car_details]}


def warranty_check(soup):
    warrenty = soup.find('div', class_="nused-warranty_drive-cfs-nused-warranty__8oMUk")
    warrenty = warrenty.find('div', class_="nused-warranty_drive-cfs-nused-warranty__details__estimations__09aGE")
    warrenty = warrenty.find('div',class_="nused-warranty_drive-cfs-nused-warranty__details__estimations__details__mGGCb").text
    warrenty = warrenty.split('/')[0]#looks something like "2 years and 6 months / Unlimited kms"
    
    return warrenty
    

#apart of parse info
def find_vheicle(soup):
        vheicle = soup.find('div', class_="aside listing-left-aside single-listing_drive-listing__info-wrapper__fBl2H")
        vheicle = vheicle.find('h1', class_="carInfo_drive-cfs__car-info__listing-details__name___R2if").text
        return vheicle

#apart of parse info
def find_price(soup):
    try:
        price = soup.find('div',class_="priceInfoListing_drive-cfs__listing-info-price__wrapper__lJNH1")
        price = price.find('p',class_="priceInfoListing_drive-cfs__listing-info-price__original__value__gYdq7").text
    except:
        return "No price listed"
    return price




def other_infomation(soup):
    global Normal_Or_NotNormal

    specs = soup.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__wrapper__RIIAm")#this is the overall with the 8 different specs in them see below in all_specs
    all_specs = specs.findAll('li',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-item__fzCI1")#these are the individual specs (there are like 8 of them)

    all_infomation=[]
    Normal_Or_NotNormal = None#ok so there are 2 different ummm car speicifcs like theres a normal one and a 'non' normal one i guess 

    for idx, k in enumerate(all_specs):
        idx = idx+1
        if idx == 1:
            Kilometers = k.find('div',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-details__6M8L2")
            Kilometers = Kilometers.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text

        if idx == 2:
            Normal_Or_NotNormal = k.find('h4',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-heading__r9T0S").text

            if Normal_Or_NotNormal == "Engine":#essentailly im saying nomral is the second slot of the specs beiung "engine" else, not normal
                Normal_Or_NotNormal = True
            else:
                Normal_Or_NotNormal = False
        

        #When Normal:
        if Normal_Or_NotNormal == True:
            normal_infomation = normal_info(idx,k)
            all_infomation.append(normal_infomation)
        
        #when not normal (gets slightly different infomation stored in diffetent slots)
        if Normal_Or_NotNormal == False:
            not_normal_infomation = not_normal_info(idx,k)
            all_infomation.append(not_normal_infomation)

    return [all_infomation,Normal_Or_NotNormal]#list with all info, and [1] tells us if its classified as 'normal' or not 
    #return [ [...] , [True/False]]
        
    

def normal_info(idx,k):
    if idx == 2:
        Engine_type = k.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-details__uy5Jk")
        Engine_type = Engine_type.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Engine Type",Engine_type]

    elif idx == 4:
        Body_Type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Body Type:",Body_Type]

    elif idx == 5:
        Drive_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Drive Type:",Drive_type]

    elif idx == 6:
        Fuel_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Fuel Type:",Fuel_type]

    elif idx == 7:
        Fuel_efficiency =k.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Fuel Efficiency:",Fuel_efficiency]

    elif idx == 8:
        Transmission = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Transmission:",Transmission]

def not_normal_info(idx,k):
    
    if idx == 2:
        year = k.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-details__uy5Jk")
        year = year.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        try:
            years = 2025 - int(year.split(' ')[0])
            return ['Year:',years]
        except ValueError:
            return ['Year:',"Unknown"]

    if idx == 3:
        Engine_type = k.find('div', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-details__uy5Jk")
        Engine_type = Engine_type.find('p', class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Engine Type:",Engine_type]

    
    elif idx == 5:
        Body_Type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Body Type:",Body_Type]

    elif idx == 6:
        Fuel_type = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Fuel Type:",Fuel_type]


    elif idx == 7:
        Transmission = k.find('p',class_="listing-specs-and-nused_drive-cfs__listing-specs__spec-name-info__j4TP4").text
        return ["Transmission:",Transmission]


def find_year(soup):
    try:
        main_content = soup.find('div', class_="main-content")

        specs_tab_container = main_content.find('div', class_="listing-details-tabs_d-cfs-listing-details-tabs__tab-container__07jlF")

        specs_tab = specs_tab_container.find_all('div', class_="listing-details-tabs_d-cfs-listing-details-tabs__tab-container__content__SA_4V")[2]  # Index 2 = "Specs"

        for feature in specs_tab.find_all('div', class_="feature_drive-cfs__listing__feature__wrapper__Sdpnj"):
            name = feature.find('div', class_="feature_drive-cfs__listing__feature__name__xtWoi")
            if name and name.text.strip() == "Year":
                value = feature.find('span', class_="feature_drive-cfs__listing__feature__value-label__pfDJo")
                if value:
                    return value.text.strip()
    except:
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
    driver = webdriver.Chrome()

    list_of_car_brands = list_car_brands(filee)
    all_car_data = [] 

    for i in list_of_car_brands:
        cars_for_brand = main(i)

        for car_dict in cars_for_brand:
            brand = list(car_dict.keys())[0]
            all_car_details = car_dict[brand][0]
            all_car_details['brand'] = brand
            all_car_data.append(all_car_details)
        
        # break ###
    ALLDATAframe = pd.DataFrame(all_car_data)
    x = []
    cols = ALLDATAframe.columns.tolist() 
    x.append('brand')
    for h in cols:
        if h != 'brand':
            x.append(h)
    ALLDATAframe = ALLDATAframe[x]
    ALLDATAframe.to_excel("Second_Hand_Car_Data.xlsx", index=False)
    print(f"How many cars: {len(ALLDATAframe)}.")

print('quit')
driver.quit()
