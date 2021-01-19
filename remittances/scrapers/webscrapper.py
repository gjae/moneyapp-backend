import re
import requests
from bs4 import BeautifulSoup


class ScrapperResponse:

    def __init__(self, headers, status_code, body):
        self.headers = headers
        self.status_code = status_code
        self.body = body
        self.soup = BeautifulSoup(self.body, features='html.parser')

    def __getattr__(self, item):
        """
        Retorna un objeto con el finder del beautifulsoup

        :param item:
        :return:
        """
        parseString = self.parseMethodUsingCamelcase(item)
        getHtml = None

        if item in dir(self):
            getHtml = getattr(self, item)(self.soup)
        else:
            getHtml = self.soup.find(class_=parseString)

        if getHtml is None:
            return None

        return self.getResponseObject(getHtml)

    def getById(self, id):
        """
        Busca el nodo que este identificado por :id:
        :param id: ID que se desea ubicar en el documento
        :return
        """
        htmlNode = self.soup.find(id=id)

        return self.getResponseObject(htmlNode)

    def getResponseObject(self, htmlNode):
        """
        Retorna una nueva instancia de si misma a partir del nodeo html que ingresa

        :param htmlNode:
        :return:
        """
        currentClassObject = self.__class__(
            headers=self.headers,
            status_code=self.status_code,
            body=htmlNode.prettify()
        )

        return currentClassObject

    def findByCssClassName(self, className=''):
        return self.soup.find(class_=className)

    def getTextChild(self):
        """
        Retorna el texto contenido en un nodo ubicado en el body

        :return str:
        """
        return self.soup.get_text()

    def getTextClear(self):
        text = self.getTextChild()
        text = text.replace("\n", "")

        return text.strip()

    def prettyOut(self):
        self.soup.prettify()

    def parseMethodUsingCamelcase(self, string, glue="-"):
        matches = re.findall('[A-Z][^A-Z]*', string)
        response = [word.lower() for word in matches]

        return glue.join(response)


class Scrapper:
    urls_scrappers = []
    in_sequence = 0
    class_response = None

    def __init__(self, urls, *args, **kwargs):
        self.urls_scrappers = urls
        if 'class_response' in kwargs:
            self.class_response = kwargs['class_response']
        else:
            self.class_response = ScrapperResponse

    def setClassResponse(self, class_):
        if issubclass(class_, ScrapperResponse):
            self.class_response = class_
        else:
            raise ReferenceError("setClassResponse espera una subclase de ScrapperResponse")

    def getClassResponse(self):
        return self.class_response

    def requestToUr(self, url:str) -> ScrapperResponse:
        """
        Genera el request a la url indicada en el parametro :url

        :param url: la Url a la que se hara la peticion
        :return:
        """

        response = requests.get(url)

        return self.getClassResponse()(
            response.headers,
            response.status_code,
            response.text
        )

    def getUrlRequest(self):
        for url in self.urls_scrappers:
            yield self.requestToUr(url)

    def getFirstRequestResult(self) -> ScrapperResponse:
        """
        Retorna el resultado del request de la primera URL que encuentra en urls_scrappers

        :return:
        """
        for index in range(len(self.urls_scrappers)):
            return self.requestToUr(self.urls_scrappers[index])

        return None