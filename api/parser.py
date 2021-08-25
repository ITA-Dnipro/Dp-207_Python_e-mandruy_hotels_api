import requests
from lxml import html
from random import choice
import concurrent.futures
import json


MSG = 'Some problem with parser. Try later'
MSG_FOR_NOT_EXIST_CITY = "Such city doesn't exist"


class CustomException(Exception):
    def __init__(self, msg):
        self.msg = msg


class CityNotExists(CustomException):
    pass


class SomeProblemWithParsing(CustomException):
    pass


class Scraper():

    def __init__(self, **kwarg):
        if len(kwarg) == 1:
            self.parser = ScraperForCityHotels(**kwarg)
        else:
            self.parser = ScrapperForHotel(**kwarg)

    def parse(self):
        return self.parser.parse()


class ScraperForCityHotels():
    """
    Class for scrapping the site hotels24.ua
    """

    URL = 'https://hotels24.ua/'

    desktop_agents = [
        'Mozilla/5.0 (Window s NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) '
        'Version/10.0.1 Safari/602.2.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 '
        'Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

    def __init__(self, city):
        self.city = city

    def random_headers(self):
        return {'User-Agent': choice(self.__class__.desktop_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    def add_domen(self, url_for_detail):
        url_for_detail = self.__class__.URL + '/' + url_for_detail
        return url_for_detail

    @staticmethod
    def retrive_adress(adress):
        try:
            tmp = adress[1].split(', ')
            adress = ' '.join(tmp).strip()
            return adress
        except IndexError:
            return ''

    def request(self, url):
        """
        Takes url and send request to the url and returns tree of elements DOM
        """
        try:
            response = requests.get(url, headers=self.random_headers())
            if response.status_code == 200:
                tree = html.fromstring(response.text)
                return tree
            else:
                raise SomeProblemWithParsing(MSG)
        except requests.exceptions.RequestException:
            raise SomeProblemWithParsing(MSG)

    def find_url_for_cities(self, url):
        """
        Find the appropriate url for cities list
        """
        tree = self.request(url)
        href = tree.xpath('//div[@class = "panel active"]/ul/li/a/@href')
        if href:
            url = 'https:' + href[-1]
            return url
        else:
            raise SomeProblemWithParsing(MSG)

    @staticmethod
    def check_data(data):
        """
        Check if list of data is empty than return empty string, else return necessary data
        """
        try:
            data = data[0]
            return data
        except IndexError:
            return ''

    def find_detail(self, href):
        """
        Find necessary informatiom about hotel and pack it into dict
        """
        url = self.add_domen(href)
        tree = self.request(url)
        detail = tree.xpath('//*[@id="hotel-description-panel-content"]/text()')
        contacts = tree.xpath('//span[@class="phone-img"]/text()')
        prices = tree.xpath('//table[@class="room-table"]/tr/td[2]/table/tr/td[2]/input/@value')
        rooms = tree.xpath('//table[@class="room-table"]/tr/td[2]/table/caption/text()')
        prices_for_rooms = dict(zip(rooms, prices))
        photo = tree.xpath('//div[@id="image_container"]/img/@src')
        name = tree.xpath('//span[@class="fn"]/text()')
        city = tree.xpath('//div[@class="hotel-line"]/a/span/strong/text()')
        adress = tree.xpath('//div[@class="hotel-line"]/a/span/text()')
        data = {}
        data['detail'] = self.__class__.check_data(detail).strip().replace('\n', '').replace('  ', '')
        data['contacts'] = self.__class__.check_data(contacts)
        data['prices'] = prices_for_rooms
        data['photo'] = 'https:' + self.__class__.check_data(photo)
        data['hotel_name'] = self.__class__.check_data(name)
        data['city'] = self.__class__.check_data(city)
        data['adress'] = self.__class__.retrive_adress(adress)
        data['href'] = href
        return data

    def find_city_url(self, url):
        """
        Find the appropriate url for the searched city
        """
        url_for_all_cities = self.find_url_for_cities(url)
        tree = self.request(url_for_all_cities)
        cities = tree.xpath('//div[@class="catalog-name-region"]/following-sibling::ul/li/a[@class="regionSmallReg"]/text()')
        hrefs = tree.xpath('//div[@class="catalog-name-region"]/following-sibling::ul/li/a[@class="regionSmallReg"]/@href')
        if hrefs and cities:
            for index, city in enumerate(cities):
                if city == self.city:
                    return self.add_domen(hrefs[index])
            else:
                raise CityNotExists(MSG_FOR_NOT_EXIST_CITY)
        else:
            raise SomeProblemWithParsing(MSG)

    def find_urls_for_hotels_in_city(self, url):
        """
        Find the list of urls for the hotels
        """
        tree = self.request(url)
        amount = len(tree.xpath('//div[@class="hotel-container "]'))
        hrefs = tree.xpath('//div[@class="hotel-container "]/div[1]/div[2]/a[1]/@href')
        amount = amount if amount <= 100 else 100
        return hrefs[:amount]

    def parse(self):
        """
        Go around urls for hotels and return json with detail info for hotels
        """
        urls = self.find_urls_for_hotels_in_city(self.find_city_url(ScraperForCityHotels.URL))
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as p:
            data = list(p.map(self.find_detail, urls))
        return json.dumps(data, ensure_ascii=False)


class ScrapperForHotel(ScraperForCityHotels):

    def __init__(self, hotel_href, date_of_arrival, date_of_departure):
        self.hotel_href = hotel_href
        self.date_of_arrival = date_of_arrival
        self.date_of_departure = date_of_departure

    def prepare_url(self):
        """
        Insert into url appropriate date of arrival and departure
        """
        url = self.add_domen(self.hotel_href) + f'?dateArrival={self.date_of_arrival}&dateDeparture={self.date_of_departure}'
        return url

    def find_detail(self, url):
        """
        Find necessary informatiom about hotel and pack it into dict
        """
        tree = self.request(url)
        prices = tree.xpath('//table[@class="room-table"]//tr/td[2]/table//tr/td[2]/table//tr/td/div/span[@class="price"]/text()')
        rooms = map(str.strip, tree.xpath('//table[@class="room-table"]//tr/td[2]/table/caption/text()'))
        data = {}
        data['prices'] = dict(zip(rooms, prices))
        return data

    def parse(self):
        url = self.prepare_url()
        data = self.find_detail(url)
        return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    d = {'hotel_href': "Гостиницы-Киева/Отель-Предслава-4942.html",
         'date_of_departure': '30.08.2021',
         'date_of_arrival': '17.08.2021'}
    a = {'city': 'Киев'}
    # print(Scraper(**a).parse())
