from django.test import TestCase

from .scrapers.webscrapper import Scrapper, ScrapperResponse
from .scrapers.monitordolar_scrapp_response import MonitordolarScrapResponse as MDR


class MockScrapperResponse(ScrapperResponse):
    pass


class MockNoInherited:
    pass


# Create your tests here.
class ScrapperTest(TestCase):

    def testScrapperResponse(self):
        resp = ScrapperResponse([], 200, "<h1 class='back-white-table'>hola mundo</h1>")
        resp = resp.BackWhiteTable

        self.assertEqual('hola mundo', resp.getTextClear())

    def testSetClassResponse(self):
        scrapper = Scrapper(urls=[''])
        scrapper.setClassResponse(MockScrapperResponse)

        self.assertTrue(issubclass(scrapper.getClassResponse(), ScrapperResponse))

    def testRaiseReferenceErrorWhenSetClassResponseDontReceiverCorrectArgument(self):
        scrapper = Scrapper(urls=[''])

        with self.assertRaises(TypeError) as expectedError:
            scrapper.setClassResponse('NO IS A RESPONSE CLASS')

        with self.assertRaises(ReferenceError) as expectedError:
            scrapper.setClassResponse(MockNoInherited)

    def testFindNodeById(self):
        response = ScrapperResponse([], 200, "<h1 class='back-white-table' id='use-id'>hola mundo</h1>")
        response = response.getById('use-id')

        self.assertIsNotNone(response)
        self.assertEqual('hola mundo', response.getTextClear())