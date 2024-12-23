import cloudscraper

from app.database import session, Titles

class MangaLib():
    def __init__(self):
        """
        Инициализирует класс MangaLib с параметрами по умолчанию.
        Устанавливает базовый URL для API манги, создает экземпляр скраппера,
        инициализирует номер страницы, задает параметры по умолчанию для запросов к API,
        и получает путь к списку манги из конфигурации текущего приложения.
        Atributes:
            _base_url (str): Базовый URL для API манги.
            _scrapper (CloudScraper): Экземпляр CloudScraper.
            _page (int): Текущий номер страницы для пагинации.
            _params (dict): Параметры по умолчанию для запросов к API.
            _path (str): Путь к списку манги из конфигурации приложения.
        """
        
        self._base_url: str = "https://api.mangalib.me/api/manga"
        self._scrapper: cloudscraper.CloudScraper = cloudscraper.create_scraper()
        self._page: int = 1
        self._params: dict[str, any] = {
            "fields[]": ["rate", "rate_avg", "userBookmark"],
            "seed": "8cf96cfb30f43bf7478f43ba8a50641c",
            "site_id[]": 1,
            "target_id": 5064,
            "target_model": "team",
        } # Адрес страницы Dead Inside Team на mangalib.me
    

    def update_data(self) -> None:
        """
        Парсит данные из сайта mangalib.me и записывает их в файл
        """

        while True:
            self._params["page"] = self._page
            response = self._scrapper.get(self._base_url, params=self._params).json()
            if response.get("data"):
                page_data = response.get("data")
                for data in page_data:
                    name = {"ru_name": "", "en_name": "", "jp_name": ""}
                    if data.get("rus_name"):
                        name["ru_name"] = data.get("rus_name")
                    if data.get("eng_name"):
                        name["en_name"] = data.get("eng_name")
                    name['jp_name'] = data.get("name")
                    session.add(Titles(**name))

            self._page += 1
            if response.get("meta").get("has_next_page"):
                continue
            break
        session.commit()
    
    def get_manga_list(self) -> list[str]:
        """
        Читает данные из файла и возвращает русское название манги, но если нет то японское
        
        Keyword arguments:
        argument -- description
        Return: list[str]
        """
        
        titles = session.query(Titles).all()
        
        return [title.ru_name if title.ru_name else title.jp_name for title in titles]

if __name__ == "__main__":
    mangalib = MangaLib()
    manga = mangalib.get_manga_list()
    print(manga)