import urllib.parse
import requests
import urllib
import os

from dotenv import load_dotenv
load_dotenv(override=True)

class Discord:
    def __init__(self):
        """
        Класс для работы с API Discord. Используется для авторизации пользователя.
        """
        self.code: str = None
        self._BASE_AUTH_URL: str = os.getenv("BASE_AUTH_URL")
        self._API_ENDPOINT: str = os.getenv("API_ENDPOINT")
        self._CLIENT_ID: str = os.getenv("CLIENT_ID")
        self._CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
        self._REDIRECT_URI: str = os.getenv("REDIRECT_URI")
        self._SERVER_ID: str = os.getenv("SERVER_ID")
        self._scope: str = os.getenv("scope")
        self._ROLE_ID: str = os.getenv("ROLE_ID")

        self._params = {
            "client_id": self._CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self._REDIRECT_URI,
            "scope": self._scope,
        }
        self._headers: dict[str, str] = None
        
        self._access_token: str = None
        self._refresh_token: str = None

    def get_tokens(self) -> tuple[str, str]:
        """
        Возвращает кортеж с access_token и refresh_token для более удобного использование.       
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        
        return (self._access_token, self._refresh_token)
    
    def generate_login_link(self) -> str:
        """Генерирует ссылку для авторизации пользователя с нужными параметрами.
        
        Keyword arguments:
        argument -- description
        Return: ссылка для авторизации пользователя
        """
        
        return f"{self._BASE_AUTH_URL}?{urllib.parse.urlencode(self._params)}"

    def _token_api(self, data: dict[str, str]) -> dict:
        """
        Выполняет запрос к API Discord с переданными данными.
        
        Keyword arguments:
        argument -- dict[str, str] -- данные для запроса к API Discord
        Return: dict -- ответ от API Discord в формате JSON
        """
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(
            url=f"{self._API_ENDPOINT}/oauth2/token",
            data=data,
            headers=headers,
            auth=(self._CLIENT_ID, self._CLIENT_SECRET)
        )
        return r.json()

    def get_token(self, code: str) -> dict:
        """
        Получает access_token и refresh_token для пользователя и сохраняет их в переменные класса.
        
        Keyword arguments:
        argument -- code -- код авторизации полученный после перехода пользователя по ссылке и авторизации
        Return: dict -- статус выполнения запроса.
        """
        
        data_to_api = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self._REDIRECT_URI,
        }
        
        data = self._token_api(data=data_to_api)
        self._access_token = data.get("access_token")
        self._refresh_token = data.get("refresh_token")
        self._headers = {
            "Authorization": f"Bearer {self._access_token}"
        }
        
        return {"status": "success", "message": "Token has been generated."}

    def _refresh_token(self) -> None:
        """Если access_token устарел, обновляет его с помощью refresh_token.
        
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        
        data_to_api = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }

        return self._token_api(data=data_to_api)
    

    def _get_base_info(self) -> dict:
        # username, user_id, avatar
        r = requests.get(f"{self._API_ENDPOINT}/users/@me", headers=self._headers).json()
        return {"username": r.get("username"), "user_id": r.get("id"), "avatar": r.get("avatar")}

    def _get_username(self) -> str:
        """
        Получает имя пользователя в Discord.
        """
        r = requests.get(f"{self._API_ENDPOINT}/users/@me", headers=self._headers)
        return r.json().get("username")

    def _get_avatar(self) -> str:
        """
        Получает аватар пользователя в Discord.
        """
        r = requests.get(f"{self._API_ENDPOINT}/users/@me", headers=self._headers)
        return r.json().get("avatar")
    
    def _get_roles_in_server(self) -> list[str]:
        """
        Получает все роля которые есть у пользователя на сервере.
        """
        
        r = requests.get(f"{self._API_ENDPOINT}/users/@me/guilds/{self._SERVER_ID}/member", headers=self._headers)
        return r.json()['roles']
    
    def _check_role(self) -> bool:
        """Проверяет есть ли среди ролей пользователя роль DIT.
        """
        
        roles: list[str] = self._get_roles_in_server()
        print(self._ROLE_ID, roles)
        return self._ROLE_ID in roles
    
    def login(self, code: str) -> dict[str, str]:
        """
        Выполняет авторизацию пользователя и проверяет наличие роли DIT.
        
        Keyword arguments:
        code: str -- код авторизации полученный после перехода пользователя по ссылке.
        dict[str, str]: Статус выполнения запроса.
        """
        
        self.get_token(code=code)
        if self._check_role():  
            base_info = self._get_base_info()
            return {"status": "success", "message": "You are authorized.", "username": base_info["username"], "avatar": base_info["avatar"], "user_id": base_info["user_id"]}
        return {"status": "error", "message": "You are not authorized."}

    def get_user_data(self, access_token: str) -> dict:
        """
        возвращает username, avatar, user_id пользователя.
        
        Keyword arguments:
        access_token: str -- access_token пользователя.
        Return: dict -- данные пользователя.
        """
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        try:
            r = requests.get(f"{self._API_ENDPOINT}/users/@me", headers=headers).json()
            return {"username": r.get("username"), "user_id": r.get("id"), "avatar": r.get("avatar")}
        except:
            return {"status": "error", "message": "Invalid access_token."}