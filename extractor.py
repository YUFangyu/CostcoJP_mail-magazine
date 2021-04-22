import itertools
import os
import re
# from googletrans import Translator
# translator = Translator()

from google.cloud import translate_v2 as translate


def isMeasure(word):
    subStrings = []
    Measurement = ['mm','cm','m', 'ml','L','g','kg','°C']
    numbers = re.findall('[0-9]+', word)
    for number in numbers:
        index = int(word.find(number))
        length = int(len(number))
        subString = word[index+length: index+length+2]
        subStrings.append(subString)
        
    if any(unit in subStrings for unit in Measurement):
        return True
    else:
        return False

class Extractor:
    # path = os.getcwd()
    # os.chdir(path)
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "Google_Translator_key.json"
    
    
    def __init__(self, OCRlist)-> list:
        self.OCRlist = OCRlist
    
    def detect_lang(self):        
        contentDict = {}
        
    
        # os.chdir(os.getcwd())
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "Google_Translator_key.json"
        
        translate_client = translate.Client()
        for index, word in enumerate(self.OCRlist):
            # langTag = translator.detect(word).lang
            result = translate_client.detect_language(word)
            langTag = result["language"]

            if langTag == 'zh-TW' or langTag == 'zh-CN':
                langTag = 'ja'
            contentDict[word] = index, langTag
        return contentDict


    def IndexSlice(self):
        contentDict = self.detect_lang()
        # jpEnd_index = 0 
        # price_index = 0 
        # period_index = 0
                
        for text, info in contentDict.items():
            index, langTag = info
            YenMark = ['¥', 'Y', '半', '辛']
            if any(currency in text for currency in YenMark):
                price_index = index
        
        for text in reversed(self.OCRlist):
            if '/' in text or '販売' in text:
                period_index = self.OCRlist.index(text)
                break
        
        nameDict = dict(itertools.islice(contentDict.items(), 0, price_index))
        
        Measurement = ['mm','cm','m', 'ml','L','g','kg','°C']
        for text, info in reversed(nameDict.items()):
            index, langTag = info
            # if langTag != 'ja' and any(char.isdigit() for char in text) and any(unit in text for unit in Measurement):
            if langTag != 'ja' and isMeasure(text) == True:
                jpEnd_index = index
                break
            elif langTag == 'ja':
                jpEnd_index = index
                break
#             else:
#                 jpEnd_index = 1
#             break

        return jpEnd_index, price_index, period_index
        
    def price(self):
        jpEnd_index, price_index, period_index = self.IndexSlice()
        priceTag = self.OCRlist[price_index]
        try:
            priceTag = priceTag.replace('半','¥').replace('辛','¥').replace('Y', '¥')
        except:
            None
        YenMark = priceTag.rindex('¥')
        price = priceTag[YenMark:]
        return price       
    
    def jpName(self):
        contentDict = self.detect_lang()
        jpEnd_index, _, _ = self.IndexSlice()
        jpName = ' '.join(list(dict(itertools.islice(contentDict.items(), 0, jpEnd_index+1)).keys()))
        return jpName
    
    def enName(self):
        contentDict = self.detect_lang()
        jpEnd_index, price_index, _ = self.IndexSlice()
        enName = ' '.join(list(dict(itertools.islice(contentDict.items(), jpEnd_index+1, price_index)).keys()))
        return enName
        
    def period(self):
        _, _, period_index = self.IndexSlice()
        period = self.OCRlist[period_index]
        try:
            period = period.replace('|','')
        except:
            None
            
        return period
    
    def description(self):
        contentDict = self.detect_lang()
        _, price_index, period_index = self.IndexSlice()
        description = ' '.join(list(dict(itertools.islice(contentDict.items(), price_index+1, period_index-1)).keys()))
        if len(description) == 0:
            description = 'No description'
        return description

    def itemInfo(self):
        price = self.price()
        jpName = self.jpName()
        enName = self.enName()
        period = self.period()
        description = self.description()
        
        return jpName,enName,price,period,description
    
    def __str__(self):
        jpName,enName,price,period,description = self.itemInfo()
        return "jpName: {}\nenName: {}\nPrice: {}\nPeriod: {}\nDescription: {}\n\n\n".format(jpName,enName,price,period,description)



'''test

textList = ['СОНО', 
'ソフトクーラーバッグ', 
'24缶収納', 
'24 CAN SOFT COOLER', 
'半6,680', 
'ITEM# 2621058', 
'販売中全倉庫店対象 NEW']

Costco = Extractor(textList)
print(Costco)
'''