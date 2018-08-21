import pandas as pd
import time
import datetime
import csv
import os
import sys
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging

logging.basicConfig(filename='osaka_180825.log', level=logging.INFO)

# __name__はこのモジュールの名前
logger = logging.getLogger(__name__)

options = Options()
options.binary_location = '/usr/bin/google-chrome'
options.add_argument('--headless')
options.add_argument('--window-size=1280,1024')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-web-security')
#options.add_argument('--no-sandbox')
options.add_argument('--load-images=false')
options.add_argument('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/67.0.3396.87 Safari/537.36')
driver = webdriver.Chrome(executable_path='/home/ubuntu/bin/chromedriver', chrome_options=options)

area_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "area.PNG")
house_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "house.PNG")


def get_next_page(url):
    while True:
        try:
            driver.get(url)
        except NoSuchSession:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    driver.maximize_window()
    while True:
        try:
            next_btn = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@data-id="SearchResultsPagination"]/li[3]/a[@class="_1ip5u88"]'))
            )
        except NoSuchElementException:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    driver.implicitly_wait(10)
    next_btn.click()
    n_url = driver.current_url

    return n_url

def get_urls(url):
    urls = []
    while True:
        try:
            driver.get(url)
        except NoSuchSession:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    driver.maximize_window()
    driver.implicitly_wait(30)
    # <div class="_1cjnzjo">
    # <a href="/rooms/22413053?location=Kyoto%2C%20Kyoto%20Prefecture%2C%20Japan&amp;guests=4&amp;adults=4&amp;children=0&amp;toddlers=0&amp;infants=0&amp;check_in=2018-07-28&amp;check_out=2018-07-29" target="listing_22413053" rel="noopener" data-check-info-section="true" class="_1bxi5o0"><div class="_1raslrn">
    html_source = driver.page_source
    soup= BeautifulSoup(html_source, 'html.parser')
    while True:
        try:
            house_blocks = soup.find_all('div', class_="_1cjnzjo")
        except:
            continue
        else:
            break
    # <div class="propertyBlock__mainArea" onclick="window.open('/syuuekibukken/kansai/osaka/dim1003/1413046/show.html')">
    for house_block in house_blocks:
        href = house_block.find('a').get('href')
        # <a href="/rooms/7520064?location=Kyoto%2C%20Kyoto%20Prefecture%2C%20Japan&amp;check_in=2018-08-25&amp;check_out=2018-08-26" 
        
        if urljoin(BASE_URL, href) not in urls:
            urls.append(urljoin(BASE_URL, href))
            driver.save_screenshot(area_png)
            
    return urls


def scrape(url):

    """
    
    'owner_id' : 4319509
    'title' : 和室ツインルーム
    'location'
    'price/guests'
    'total_price/JPY'
    'cleaning_fee'
    'service_fee'
    'only_price'
    'thismonth_rate'
    'nextmonth_rate'
    'reviews'
    'superhost' : 0 or 1
    'guests' : 2
    'bedrooms' : 2
    'beds' : 2
    'bathrooms' : 2共用
    'thismonth_bookings' : 30
    'nextmonth_bookings' : 5
    'date'
    'datetime'
    'url' : 'https://www.airbnb.jp/rooms/4319509'
    
    """

    data = {}
    notFound = []
    while True:
        try:
            driver.get(url)
            driver.maximize_window()
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@itemprop="name"]//span[@class="_12ei9u44"]/h1[@tabindex="-1"]'))
            )
        except NoSuchElementException:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    html_source = driver.page_source
    soup= BeautifulSoup(html_source, 'html.parser')
    driver.save_screenshot(house_png)

    # 初期化
    for r in  [

        'owner_id', 'title', 'location', 'price/guests', 'total_price/JPY', 'cleaning_fee','service_fee', 'only_price', \
        'thismonth_rate', 'nextmonth_rate', 'reviews', 'superhost', 'guests',  'bedrooms', 'beds', 'bathrooms', 'thismonth_bookings',  'nextmonth_bookings', 'date', 'datetime', 'url'
        
        ]:
        data[r] = None
    
    try:
        data['owner_id'] = re.search(r'(\d+)', url).group(1)
    except Exception:
        notFound.append('owner_id')
    print('owner_id:', data['owner_id'])

    #listing_title
    try:
        data['title'] = driver.find_element_by_xpath('//div[@itemprop="name"]//span[@class="_12ei9u44"]/h1[@tabindex="-1"]').text
    except Exception:
        notFound.append('title')
    print('title:', data['title'])

    # location
    try:
        data['location'] = driver.find_element_by_xpath('//*[@id="summary"]/div/div[1]/div[1]/div/div[1]/div[2]/div/a/div').text
    except Exception:
        notFound.append('location')
    print('location:', data['location'])

    # number_of_guests
    # //*[@id="summary"]/div/div[1]/div[2]/div/div[1]/div/div[2]
    # <div class="_1thk0tsb"><span class="_fgdupie">5 guests</span></div>
    try:
        tmp = driver.find_element_by_xpath('//*[@id="summary"]/div/div[1]/div[2]/div/div[1]/div/div[2]/span').text
        _tmp = tmp.replace(' ','')
        #print(_tmp)
        #import pdb; pdb.set_trace()
        try:
            m = re.match('\d*', _tmp)[0]
            data['guests'] = int(m)
        except:
            if m == '16+':
                m_n16 = m.strip('+')
                data['guests'] = int(m_n16)
            else:
                data['guests'] = int(m)
    except Exception:
        notFound.append('guests')
    print('guests:', data['guests'])

    # number_of_bedrroms
    try:
        tmp = driver.find_element_by_xpath('//*[@id="summary"]/div/div[1]/div[2]/div/div[2]/div/div[2]/span').text
        _tmp = tmp.replace(' ','')
        #print(_tmp)
        match = re.search(r'bedrooms', _tmp)
        if match:
            data['bedrooms'] = _tmp.strip('bedrooms')
        else:
            data['bedrooms'] = _tmp.strip('bedroom')
    except Exception:
        notFound.append('bedrooms')
    print('bedrooms:',  data['bedrooms'])

    # number_of_beds
    try:
        tmp = driver.find_element_by_xpath('//*[@id="summary"]/div/div[1]/div[2]/div/div[3]/div/div[2]/span').text
        _tmp = tmp.replace(' ','')
        #print(_tmp)
        match = re.search(r'beds', _tmp)
        if match:
            data['beds'] = _tmp.strip('beds')
        else:
            data['beds'] = _tmp.strip('bed')
    except Exception:
        notFound.append('beds')
    print('beds:', data['beds'])

    # number_of_bathrroms
    try:
        tmp = driver.find_element_by_xpath('//*[@id="summary"]/div/div[1]/div[2]/div/div[4]/div/div[2]/span').text
        _tmp = tmp.replace(' ','')
        #print(_tmp)
        try:
            #import pdb; pdb.set_trace()
            m = re.match('\d*', _tmp)[0]
            data['bathrooms'] = int(m)
        except:
            try:
                m = re.match('\d*.\d*', _tmp)[0]
                data['bathrooms'] = int(m)
            except:
                data['bathrooms'] = -tmp

        """
        match = re.search(r'sharedbaths', _tmp)
        if match:
            data['bathrooms'] = _tmp.strip('sharedbaths')
        else:
            match = re.search(r'baths', _tmp)
            if match:
                data['bathrooms'] = _tmp.strip('baths')
            else:
                match = re.search(r'private', _tmp)
                if match:
                    data['bathrooms'] = _tmp.strip('private')
                else:
                    data['bathrooms'] = _tmp.strip('bath')
                    """
    except Exception:
        notFound.append('bathrooms')
    print('bathrooms:', data['bathrooms'])

    # check if total_price includes "cleaning fee" or not
    while True:
        try:
            time.sleep(random.randint(31,34))
            cf = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="book_it_form"]/div[2]/div[2]/div[1]/div[1]/span/span'))
            )
        except NoSuchElementException:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    #print(cf.text)
    cf_text = cf.text
    if cf_text == 'Cleaning fee':
        # ex. 'https://www.airbnb.com/rooms/24925453?location=Kyoto%2C%20Kyoto%20Prefecture%2C%20Japan&check_in=2018-08-25&check_out=2018-08-26'
        # total_price/JPY
        while True:
            try:
                time.sleep(random.randint(31,34))
                tp = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="book_it_form"]/div[2]/div[4]/div/div[2]/span/span/span[contains(text(), "¥")]'))
                )
            except NoSuchElementException:
                print(f'\n{traceback.format_exc()}')
                continue
            else:
                break
        try:
            tmp = tp.text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            total_price = int(_tmp)
            data['total_price/JPY'] = total_price
        except Exception:
            data['total_price/JPY'] = 0
        print('total_price/JPY:', data['total_price/JPY'])

        # only_price
        try:
            tmp = driver.find_element_by_xpath('//span[@class="_doc79r"]/span[contains(text(), "¥")]').text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            only_price = int(_tmp)
            data['only_price'] = only_price
        except Exception:
            data['only_price'] = 0
        print('only_price:', data['only_price'])
        
        # cleaning_fee
        try:
            tmp = driver.find_element_by_xpath('//*[@id="book_it_form"]/div[2]/div[2]/div[1]/div[2]/span/span/span[contains(text(), "¥")]').text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            cleaning_fee = int(_tmp)
            data['cleaning_fee'] = cleaning_fee
        except Exception:
            data['cleaning_fee'] = 0
        print('cleaning_fee:', data['cleaning_fee'])
    
        # service_fee
        try:
            tmp = driver.find_element_by_xpath('//*[@id="book_it_form"]/div[2]/div[3]/div[1]/div[2]/span/span/span[contains(text(), "¥")]').text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            service_fee = int(_tmp)
            data['service_fee'] = service_fee
        except Exception:
            data['service_fee'] = 0
        print('service_fee:', data['service_fee'])
    
    else:
        # ex. # 'https://www.airbnb.com/rooms/23009242?location=Kyoto%2C%20Kyoto%20Prefecture%2C%20Japan&check_in=2018-08-25&check_out=2018-08-26'
        # total_price
        while True:
            try:
                time.sleep(random.randint(31,34))
                tp = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="book_it_form"]/div[2]/div[3]/div/div[2]/span/span/span[contains(text(), "¥")]'))
                )
            except NoSuchElementException:
                print(f'\n{traceback.format_exc()}')
                continue
            else:
                break
        try:
            tmp = tp.text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            total_price = int(_tmp)
            data['total_price/JPY'] = total_price
        except Exception:
            data['total_price/JPY'] = 0
        print('total_price/JPY:', data['total_price/JPY'])

        # only_price
        try:
            tmp = driver.find_element_by_xpath('//span[@class="_doc79r"]/span[contains(text(), "¥")]').text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            only_price = int(_tmp)
            data['only_price'] = only_price
        except Exception:
            data['only_price'] = 0
        print('only_price:', data['only_price'])

        # cleaning_fee
        data['cleaning_fee'] = 0
        print('cleaning_fee:', data['cleaning_fee'])

        # service_fee
        try:
            tmp = driver.find_element_by_xpath('//*[@id="book_it_form"]/div[2]/div[2]/div[1]/div[2]/span/span/span[contains(text(), "¥")]').text
            _tmp = tmp.lstrip('¥').replace(' ','').replace(',','')
            service_fee = int(_tmp)
            data['service_fee'] = service_fee
        except Exception:
            data['service_fee'] = 0
        print('service_fee:', data['service_fee'])
    
    # price/guests
    try:
        tmp = round(data['total_price/JPY'] / data['guests'], 2) 
        data['price/guests'] = float(tmp)
    except:
        notFound.append('price/guests')

# number_of_booking
    # occupancy_rate
    while True:
        try:
            checkin_btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="checkin"]'))
            )
        except NoSuchElementException:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    checkin_btn.click()
    time.sleep(random.randint(31,34))
    html_source = driver.page_source
    soup= BeautifulSoup(html_source, 'html.parser')
    div_n1_m1 = soup.find('div', class_="_6vx1r9")
    div_n2_m1 = div_n1_m1.find('div', class_="_697bgjb")
    #import pdb; pdb.set_trace()
    div_n3_m1 = div_n2_m1.find('div', class_="_1lds9wb")
    div_n4_m1 = div_n3_m1.find('div', class_="_gahfr9")
    table_m1 = div_n4_m1.find('table', class_="_p5jgym")
    #trs = table.tbody.find_all('tr')
    trs_m1 = table_m1.tbody
    try:
        m_oc_m1 = re.findall(r'("_z39f86g")', str(trs_m1))
        if m_oc_m1:
            data['nextmonth_bookings'] = int(len(m_oc_m1))
        else:
            data['nextmonth_bookings'] = 0
    except:
        data['nextmonth_bookings'] = 0
    print('nextmonth_bookings', data['nextmonth_bookings'])

    try:
        m_va_m1 = re.findall(r'("_12fun97")', str(trs_m1))
        if m_va_m1:
            tmp_m1 = int(len(m_oc_m1)) + int(len(m_va_m1))
            _tmp_m1 = int(len(m_oc_m1)) / float(tmp_m1)
            data['nextmonth_rate'] = '{:.2%}'.format(_tmp_m1)
        else:
            notFound.append('nextmonth_rate')
    except:
        if data['nextmonth_bookings'] != 0:
            _tmp_m2 = int(len(m_oc_m2)) / float(len(m_oc_m2))
            data['nextmonth_rate'] = '{:.2%}'.format(_tmp_m2)
        else:
            notFound.append('nextmonth_rate')
    print('nextmonth_rate', data['nextmonth_rate'])

    ###########################################################################################################
    ################ move to thismonth calendar ###############################################################
    ###########################################################################################################
    #//*[@id="book_it_form"]/div[1]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[1]/button[2]
    #<div class="_14676s3" role="region" tabindex="-1">
    ##<div class="_1dcc3hk0">
    ###<button class="_32wq2a2" type="button" aria-label="Move backward to switch to the previous month."></button>
    ###<button class="_121ogl43" type="button" aria-label="Move forward to switch to the next month.">
    while True:
        try:
            this_month_btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="_14676s3"]/div[@class="_1dcc3hk0"]/button[@class="_32wq2a2"]'))
            )
        except NoSuchElementException:
            print(f'\n{traceback.format_exc()}')
            continue
        else:
            break
    this_month_btn.click()
    time.sleep(random.randint(31,34))
    #import pdb; pdb.set_trace()
    html_source = driver.page_source
    soup= BeautifulSoup(html_source, 'html.parser')
    div_n1_m2 = soup.find('div', class_="_6vx1r9")
    div_n2_m2 = div_n1_m2.find('div', class_="_697bgjb")
    div_n3_m2 = div_n2_m2.find('div', class_="_1lds9wb")
    div_n4_m2 = div_n3_m2.find('div', class_="_gahfr9")
    table_m2 = div_n4_m2.find('table', class_="_p5jgym")
    #trs = table.tbody.find_all('tr')
    trs_m2 = table_m2.tbody
    try:
        m_oc_m2 = re.findall(r'("_z39f86g")', str(trs_m2))
        if m_oc_m2:
            data['thismonth_bookings'] = int(len(m_oc_m2))
        else:
            data['thismonth_bookings'] = 0
    except:
        data['thismonth_bookings'] = 0
    print('thismonth_bookings', data['thismonth_bookings'])

    try:
        m_va_m2 = re.findall(r'("_12fun97")', str(trs_m2))
        if m_va_m2:
            tmp_m2 = int(len(m_oc_m2)) + int(len(m_va_m2))
            _tmp_m2 = int(len(m_oc_m2)) / float(tmp_m2)
            data['thismonth_rate'] = '{:.2%}'.format(_tmp_m2)
        else:
            if data['thismonth_bookings'] != 0:
                _tmp_m2 = int(len(m_oc_m2)) / float(len(m_oc_m2))
                data['thismonth_rate'] = '{:.2%}'.format(_tmp_m2)
            else:
                notFound.append('thismonth_rate')
    except:
        notFound.append('thismonth_rate')
    print('thismonth_rate', data['thismonth_rate'])


    # reviews
    try:
        tmp = driver.find_element_by_xpath('//*[@id="reviews"]/div/div/div/section/div[1]/div[1]/div/div[1]/div/div/div/div/span/h2/span').text
        if tmp == 0:
            data['reviews'] = 0
        else:
            try:
                #import pdb; pdb.set_trace()
                m = re.match('\d*', tmp)[0]
                data['reviews'] = int(m)
            except:
                data['reviews'] = tmp
    except Exception:
        data['reviews'] = 0
    print('reviews:', data['reviews'])
    
    # superhost
    try:
        tmp = driver.find_element_by_xpath('//*[@id="host-profile"]/div/div/section/div[2]/div[2]/div[1]/span[1]').text
        m = re.search(r'(.*is a Superhost)', tmp)[0]
        if m:
            data['superhost'] = 1
        else:
            data['superhost'] = 0
    except Exception:
        data['superhost'] = 0
    print('superhost:', data['superhost'])

    # date
    data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')

    if len(notFound)!=0:
        pass
    
    # datetime
    data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if len(notFound)!=0:
        pass
    
    # listing url
    data['url'] = driver.current_url

    return data



BASE_URL = 'https://www.airbnb.com'
date_of_checkin = '2018-08-25' # ex. '2018-08-25'
date_of_checkout = '2018-08-26' # ex. '2018-08-26'

if __name__ == '__main__':
    datas = []
    start = time.time()
    
    # kyoto
    # 'https://www.airbnb.com/s/Kyoto--Kyoto-Prefecture--Japan/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJ8cM8zdaoAWARPR27azYdlsA&query=Kyoto%2C%20Kyoto%20Prefecture%2C%20Japan&checkin=2018-08-25&checkout=2018-08-26&min_beds=1&min_bedrooms=1&min_bathrooms=1&allow_override%5B%5D='
    # osaka
    # 'https://www.airbnb.com/s/Osaka--Osaka-Prefecture--Japan/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJ4eIGNFXmAGAR5y9q5G7BW8U&query=Osaka%2C%20Osaka%20Prefecture%2C%20Japan&checkin=2018-08-25&checkout=2018-08-26&min_beds=1&min_bedrooms=1&min_bathrooms=1&price_min=2829&price_max=77246&allow_override%5B%5D=&s_tag=P0-NFW7j'
    # 'https://www.airbnb.com/s/Osaka--Osaka-Prefecture--Japan/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJ4eIGNFXmAGAR5y9q5G7BW8U&query=Osaka%2C%20Osaka%20Prefecture%2C%20Japan&checkin=2018-08-25&checkout=2018-08-26&min_beds=1&min_bedrooms=1&min_bathrooms=1&price_min=1755&price_max=87217&allow_override%5B%5D=&s_tag=xepuKXHN'
    URL_frag1 = r'https://www.airbnb.com/s/Osaka--Osaka-Prefecture--Japan/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJ4eIGNFXmAGAR5y9q5G7BW8U&query=Osaka%2C%20Osaka%20Prefecture%2C%20Japan'
    URL_checkin = r'&checkin='
    URL_checkout = r'&checkout='
    URL_frag2 = r'&min_beds=1&min_bedrooms=1&min_bathrooms=1'    
    URL_price_min = r'&price_min='
    URL_price_max = r'&price_max='
    URL_frag3 = r'&allow_override%5B%5D=&s_tag=xepuKXHN'

    crawl_number = 1
    
    price_1100 = 1100
    price_5000 = 5000

    first_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(price_1100) + URL_price_max + str(price_5000) + URL_frag3
    current_url = first_list_url
    print('min_price:'+ str(price_1100) +' max_price:' + str(price_5000))
    print('■', current_url)
    urls = []
    #time.sleep(random.randint(3,5))
    #urls.extend(get_urls(current_url))
    
    while True:
        time.sleep(random.randint(3,5))
        urls.extend(get_urls(current_url))
        try:
            time.sleep(random.randint(3,5))
            current_url = get_next_page(current_url)
            print('■', current_url)
        except:
            break
    

    # tests
    #for min_price in range(1100,20000,5000):
    for min_price in range(5000,40000,5000):
    #for min_price in range(5000,95000,5000):
        max_price = min_price +5000
        second_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(min_price) + URL_price_max + str(max_price) + URL_frag3
        current_url = second_list_url
        print('min_price:'+ str(min_price) +' max_price:' + str(max_price))
        print('■', current_url)
        #time.sleep(random.randint(3,5))
        #urls.extend(get_urls(current_url))
        
        while True:
            time.sleep(random.randint(3,5))
            urls.extend(get_urls(current_url))
            try:
                time.sleep(random.randint(3,5))
                current_url = get_next_page(current_url)
                print('■', current_url)
            except:
                break
        

    price_40000 = 40000
    price_100000 = 100000

    first_list_url = URL_frag1 + URL_checkin + date_of_checkin + URL_checkout + date_of_checkout + URL_frag2 + URL_price_min + str(price_40000) + URL_price_max + str(price_100000) + URL_frag3
    current_url = first_list_url
    print('min_price:'+ str(price_40000) +' max_price:' + str(price_100000))
    print('■', current_url)
    #time.sleep(random.randint(3,5))
    #urls.extend(get_urls(current_url))
    
    while True:
        time.sleep(random.randint(3,5))
        urls.extend(get_urls(current_url))
        try:
            time.sleep(random.randint(3,5))
            current_url = get_next_page(current_url)
            print('■', current_url)
        except:
            break
    
    
    print('■■', urls)
    urls_conts = len(urls)
    print('・・・', str(urls_conts) + 'th listings!')
    for house_data_url in urls:
        try:
            print('■■■', house_data_url)
            datas.append(scrape(house_data_url))
            time.sleep(random.randint(3,8))
            print('【No.'+ str(crawl_number) + '】' + house_data_url)
            crawl_number = crawl_number + 1
        except:
            print('orz >>> NO LISTING!')

    column_order = [
    
        'owner_id', 'title', 'location', 'price/guests', 'total_price/JPY', 'cleaning_fee','service_fee', 'only_price', \
        'thismonth_rate', 'nextmonth_rate', 'reviews', 'superhost', 'guests',  'bedrooms', 'beds', 'bathrooms', 'thismonth_bookings',  'nextmonth_bookings', 'date', 'datetime', 'url'
        
    ]
    if len(datas)!=0:
        df = pd.DataFrame(datas)
        df.to_csv('/home/ubuntu/bnbch/csv/bnb_osaka_180825_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv', sep=',',encoding='UTF-8',index=False, quoting=csv.QUOTE_ALL, columns=column_order)
        df.to_csv('/home/ubuntu/bnbch/csv/bnb_osaka_180825_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.tsv', sep='\t',encoding='UTF-8',index=False, quoting=csv.QUOTE_ALL, columns=column_order)
    
    end = time.time()
    print("process {0} ms".format((end - start) * 1000))
    sys.exit()
    
driver.quit()