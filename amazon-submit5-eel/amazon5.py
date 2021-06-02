from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
from datetime import datetime
import re
from selenium.webdriver import Chrome, ChromeOptions
import eel


### Chromeを起動する関数
def set_driver(driver_path,headless_flg):
    options = ChromeOptions()

    if headless_flg == True:
        options.add_argument('--headless')
    
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')  # シークレットモードの設定を付与

    return Chrome(ChromeDriverManager().install(),options=options)

time=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
log_file_name = 'log/log_{}.log'.format(time)

def log(txt):
    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[log: {}] {}'

    with open(log_file_name,'a',encoding='utf-8_sig') as f:
        f.write(logStr.format(now,txt)+'\n')
    print(logStr.format(now,txt))
    eel.view_log(logStr.format(now,txt))

def main(url):
    # url = 'https://www.amazon.co.jp/gp/bestsellers/kitchen/ref=zg_bs_kitchen_home_all?pf_rd_p=234a2e41-c662-4f1c-987f-e3b33cc421ff&pf_rd_s=center-1&pf_rd_t=2101&pf_rd_i=home&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=69W2MBGRT6S8E3WYBSCH&pf_rd_r=69W2MBGRT6S8E3WYBSCH&pf_rd_p=234a2e41-c662-4f1c-987f-e3b33cc421ff'
    if url == '':
        print('URLを入力してください。')
        eel.view_log('URLを入力してください。')
    else:
        log('処理開始')
        log('URL : {}'.format(url))
        driver = set_driver('chromedriver.exe',False)
        driver.get(url)
        sleep(3)

    p_names = []
    link_urls = []
    while True:
        for i in range(1,52):
            if i < 5:
                p_name = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a > div'.format(i)).text
                link_url = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a'.format(i)).get_attribute('href')
                p_names.append(p_name)
                link_urls.append(link_url)
            elif i == 5:
                pass
            else:
                p_name = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a > div'.format(i)).text
                link_url = driver.find_element_by_css_selector('#zg-ordered-list > li:nth-child({}) > span > div > span > a'.format(i)).get_attribute('href')
                p_names.append(p_name)
                link_urls.append(link_url)

        if len(driver.find_elements_by_css_selector('#zg-center-div > div.a-row.a-spacing-top-mini > div > ul > li.a-last > a')) > 0:
            next_page = driver.find_element_by_css_selector('#zg-center-div > div.a-row.a-spacing-top-mini > div > ul > li.a-last > a').get_attribute('href')
            driver.get(next_page)
            sleep(3)
        else:
            log('ランキング商品名と商品ページurlを取得しました。')
            break

    names = []
    prices = []
    deliveries = []
    asins = []
    count = 0
    success = 0
    fail = 0
    for item_url in link_urls:
        driver.get(item_url)
        sleep(4)

        try:
            name = driver.find_element_by_id('productTitle')
            names.append(name.text)

            if len(driver.find_elements_by_css_selector('#priceblock_ourprice')) > 0:
                _price = driver.find_element_by_css_selector('#priceblock_ourprice')
                price = int(_price.text.replace('￥','').replace(',',''))
                prices.append(price)
            elif len(driver.find_elements_by_css_selector('#priceblock_dealprice')) > 0:
                _price = driver.find_element_by_css_selector('#priceblock_dealprice')
                price = int(_price.text.replace('￥','').replace(',',''))
                prices.append(price)
            elif len(driver.find_elements_by_css_selector('#olp_feature_div > div.a-section.a-spacing-small.a-spacing-top-small > span > a > span.a-size-base.a-color-price')) > 0:
                _price = driver.find_element_by_css_selector('#olp_feature_div > div.a-section.a-spacing-small.a-spacing-top-small > span > a > span.a-size-base.a-color-price')
                price = int(_price.text.replace('￥','').replace(',',''))
                prices.append(price)
            else:
                price = ''
                prices.append(price)
        
            if len(driver.find_elements_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE > b')) > 0:
                if len(driver.find_elements_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span')) > 0:
                    delivery = driver.find_element_by_css_selector('#oneTimePurchaseDefaultDeliveryDate > span').text
                    deliveries.append(delivery)
                else:
                    delivery = driver.find_element_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE > b').text
                    deliveries.append(delivery)       
            elif len(driver.find_elements_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-UPSELL > b')) > 0:
                delivery = driver.find_element_by_css_selector('#mir-layout-DELIVERY_BLOCK-slot-UPSELL > b').text
                deliveries.append(delivery)
            elif len(driver.find_elements_by_css_selector('#ddmDeliveryMessage > b')) > 0:
                delivery = driver.find_element_by_css_selector('#ddmDeliveryMessage > b').text
                deliveries.append(delivery)
            elif len(driver.find_elements_by_css_selector('#availability > span.a-size-medium.a-color-state')) > 0:
                delivery = driver.find_element_by_css_selector('#availability > span.a-size-medium.a-color-state').text
                deliveries.append(delivery)
            else:
                delivery = ''
                deliveries.append(delivery)

            if len(driver.find_elements_by_css_selector('#detailBullets_feature_div > ul > li')) > 0:
                texts = driver.find_elements_by_css_selector('#detailBullets_feature_div > ul > li')
                for _text in texts:
                    pattern = r'^ASIN : B.*'
                    result = re.search(pattern,_text.text)
                    if result == None:
                        pass
                    else:
                        asin = result.group().split(':')[1].replace(' ','')
                        asins.append(asin)
            elif len(driver.find_elements_by_css_selector('#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td')) > 0:
                asin = driver.find_element_by_css_selector('#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td').text
                asins.append(asin)
            else:
                asin = ''
                asins.append(asin)
            
            log(f'{count}件目成功 : {name.text}')
            success += 1
        
        except Exception as e:
            log(f'{count}件目失敗 : {name.text}')
            log(e)
            fail += 1
        
        finally:
            # finallyは成功の時もエラーの時も関係なく必ず実行する処理。ここでは必ずcountに１をプラスして総合回数を記録する処理。        
            count += 1
    
    log('検索完了しました。')

    # driver.close()

    df = pd.DataFrame()
    df['商品名'] = p_names
    df['商品ページへのURL'] = link_urls
    df['商品名（詳細）'] = names
    df['価格（円）'] = prices
    df['発送リードタイム（納期）'] = deliveries
    df['ASIN'] = asins

    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    df.to_csv('売れ筋ランキング一覧:{}.csv'.format(time),index=True)

# if __name__ == "__main__":
#     main()
    