from decimal import Decimal
from .webscrapper import ScrapperResponse


class MonitordolarScrapResponse(ScrapperResponse):

    def BackWithTable(self, soup):
        return self.findByCssClassName('back-with-table')

    def getTextClear(self):
        text = super(MonitordolarScrapResponse, self).getTextClear()

        return text.replace("BsS", "").strip()

    def asDecimal(self):
        return Decimal(
            self.getTextClear()
        )
