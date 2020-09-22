from selenium import webdriver
from datetime import datetime
import bs4
import re
import pdfkit
import os

# SETTING UP BROWSER
browser = webdriver.Chrome('drivers/chromedriver')

# OPEN LOGIN PAGE
browser.get('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Flogin%2Fs%3Fk%3Dlogin%26page%3D4%26ref_%3Dnav_ya_signin%26_encoding%3DUTF8&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&')

# TO STOP FROM MOVING FORWARD UNTIL LOGIN IS DONE
print('\nPlease make sure that orderIDs are in the [orders.txt] file and currencyRates are in the [rates.txt] file.')
print('Please make sure date and rate be seperated by one tab space[\\t] in rates file')
print('Please do not delete those files.')
print('\nPlease login using the browser')
print('To exit the program, please press [crlt + c]\n')
done = ""

while done != 'y':
    done = input('Are you logged in? [y] = ')
    
# LIST WHERE NAMES OF FILES TO BE CONVERTED TO PDF ARE STORED
# [DOING THIS SINCE DIRECTLY CONVERTING STRING TO PDF LEADS TO FORMATING ERRORS]
files_to_convert = []

# OPENING ORDERS ID TEXT FILE
with open('orders.txt') as orderIDs:
    for orderID in orderIDs.readlines():
        if len(orderID) < 2: continue

        # REMOVING \n
        orderID = re.sub('\n', '', orderID)

        # OPEN ODERS PRINT PAGE
        url = 'https://www.amazon.com/gp/css/summary/print.html/ref=ppx_od_dt_b_print_invoice?ie=UTF8&orderID=' + orderID
        browser.get(url)

        # GETTING HTML FROM BROWSER
        page = bs4.BeautifulSoup(browser.page_source, features="lxml")
        raw_tds = page.select('td[nowrap]')

        # FORMATED DATE
        date = str(raw_tds[-2].text).split(':')[1][1:]
        date = datetime.strptime(date, '%B %d, %Y').strftime('%d/%m/%Y').lstrip("0").replace(" 0", " ")

        # FINDING CURRENT RATE FROM RATES TEXT FILE
        current_rate = 0
        with open('rates.txt') as rates:
            for rate in rates.readlines():
                if len(rate) < 2: continue

                arr = re.sub('\n', '', rate).split('\t')
                if arr[0] == str(date):
                    current_rate = float(arr[1])
                

        # USD PRICE AND CONVERTED PRICE
        usd_price = float(re.sub('\s+', '', raw_tds[-1].text[1:])[1:])
        converted_price = usd_price * current_rate
        converted_price_round = round(converted_price,2)

        # CREATE AND ADD NOTE TO HTML
        note = """
        <div id="note">
            <h4><u>NOT:</u></h4>
            İş bu faturanın ödemesi yapıldığı {} tarihindeki TCMB Amerikan Doları (USD) kuru {} TL'dir. 
            <br>
            Bu kur fiyatina göre toplam fatura tutarı {} TL'dir.
        <div>
        """.format(date, current_rate, converted_price_round)

        # GETTING ORDERS TABLE FROM HTML
        table = str(page.find('table'))

        # ADDING TO HTML
        # [DOING THIS TO REMOVE EXTRA HTML AND SCRIPT. ALSO META TAG REQUIRED TO SHOW NOTE TEXT]
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="style.css">
        </head>
            <body>
                <img src="amazon-logo-tiny._CB192256679_.gif">
                <center><h2><strong>Final Details for Order #{}</strong></h2></center>
                {}
                <center>
                    <p>To view the status of your order, return to Order Summary.</p>
                    <strong>Please note:</strong> This is not a VAT invoice.
                    <p><a href="#">Conditions of Use</a> | <a href="#">Privacy Notice</a> © 1996-2019, Amazon.com, Inc. or its affiliates</p>
                </center>
                {}
            <body>
        </html>
        """.format(orderID, table, note)
        
        # CREATE HTML FILES TO PRINT
        # [DOING THIS SINCE DIRECTLY CONVERTING STRING TO PDF LEADS TO FORMATING ERRORS]
        with open(orderID + '.html', 'w', encoding='utf8') as file:
            file.write(html_content)
        
        # ADDING FILE NAME TO CONVERT TO PDF_LIST
        files_to_convert.append(orderID + '.html')

# CONFIGURATION OF EXE PATH
path_wkhtmltopdf = 'drivers\wkhtmltopdf\\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# CREATING PDF
pdf = pdfkit.from_file(files_to_convert, 'AMAZON_ORDERS.pdf', configuration=config)

# REMOVING HTML FILES
for f in files_to_convert:
    if os.path.exists(f):
        os.remove(f)

# CLOSING BROWSER
browser.close()

# CLOSING PROGRAM
exit()