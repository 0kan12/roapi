import requests
import time

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
authurl = 'https://auth.roblox.com/v2/logout'
class new_request:
    def __init__(self, cookie: str, url: str, data=None, method="get"):
        self.cookie = cookie
        self.url = url
        self.data = data
        self.method = method
        self.response = None
        self.send_request()
    
    def send_request(self):
        """
        HTTP isteği gönderir.
        """
        try:
            request_func = getattr(requests, self.method.lower())
            self.response = request_func(self.url, params=self.data, data=self.data, headers=self.headers, cookies=self.cookies)
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
    
    def headers(self):
        """
        HTTP başlık bilgilerini döndürür.
        """
        token = token_response = requests.post(authurl, headers={'User-Agent': useragent}, cookies=self.cookies()).headers.get('x-csrf-token', '')
        return {"X-CSRF-TOKEN": token} if token else {}
    
    def cookies(self):
        """
        HTTP çerez bilgilerini döndürür.
        """
        return {".ROBLOSECURITY": self.cookie}
    
    def json(self):
        """
        Yanıtı JSON formatına dönüştürür.
        """
        if self.response:
            return self.response.json()
        else:
            return None
class delete1:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def delete_asset(self, assetid):
        """
        Roblox envanterinden bir asset'i siler.
        """
        url = f"https://www.roblox.com/asset/delete-from-inventory"
        data = {"assetId": assetid}
        new_request(self.cookie, url, data, "post")
        print("Item silindi")
    
    def delete_pass(self, passid):
        """
        Roblox oyun geçişini (gamepass) iptal eder.
        """
        url = f"https://www.roblox.com/game-pass/revoke"
        data = {"id": passid}
        new_request(self.cookie, url, data, "post")

class bilgi:
    @staticmethod
    def get_user_id(cookie):
        """
        Verilen çerez ile oturum açmış kullanıcının Roblox ID'sini döndürür.
        """
        url = "https://users.roblox.com/v1/users/authenticated"
        response = new_request(cookie, url, {}, "get")
        return response.json()['id']

    @staticmethod
    def get_info_request_url(type: str, id: int):
        """
        Belirli bir asset veya pass için bilgi istek URL'si oluşturur.
        """
        if type == "pass":
            return f"https://apis.roblox.com/game-passes/v1/game-passes/{id}/product-info"
        elif type == "asset":
            return f"https://economy.roblox.com/v2/assets/{id}/details"

    @staticmethod
    def get_info(id: int, type: str):
        """
        Belirtilen ID ve tür için bilgileri getirir (ProductId, Creator Id, PriceInRobux).
        """
        url = bilgi.get_info_request_url(type, id)
        response = requests.get(url)
        data = response.json()
        return [data['ProductId'], data['Creator']['Id'], data['PriceInRobux']]
    

    @staticmethod
    def get_user_id_by_username(username):
        """
        Verilen kullanıcı adına sahip kullanıcının Roblox ID'sini döndürür.
        """
        API_ENDPOINT = "https://users.roblox.com/v1/usernames/users"
        payload = {'usernames': [username]}
        response = requests.post(API_ENDPOINT, json=payload)
        return response.json()['data'][0]['id']
    
    @staticmethod
    def get_gamepasses(username):
        """
        Verilen kullanıcının oyun geçişlerini (pass) listeler.
        """
        user_id = bilgi.get_user_id_by_username(username)
        url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=Public&limit=50"
        response = requests.get(url)
        ids = [game['id'] for game in response.json()['data']]
        
        gamepasses = []
        for universe_id in ids:
            url = f'https://games.roblox.com/v1/games/{universe_id}/game-passes?limit=100&sortOrder=Asc'
            response = requests.get(url)
            for gamepass in response.json()['data']:
                if gamepass['price'] is not None:
                    gamepasses.append([gamepass['id'], gamepass['price']])
        
        return gamepasses

class Buyer:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def buy(self, delete: bool, id: int, type: str):
        """
        Belirtilen asset veya pass'i satın alır.
        """
        info = bilgi.get_info(id, type)
        data = {"expectedCurrency": 1, "expectedPrice": info[2], "expectedSellerId": info[1]}
        url = f"https://economy.roblox.com/v1/purchases/products/{info[0]}"
        response = new_request(self.cookie, url, data, "post")
        print(response.content)
        
        if delete:
            if type == "pass":
                delete1(self.cookie).delete_pass(id)
            elif type == "asset":
                delete1(self.cookie).delete_asset(id)
    
    def RobuxAmount(self):
        """
        Kullanıcının Robux miktarını döndürür.
        """
        url = f"https://economy.roblox.com/v1/users/{bilgi.get_user_id(self.cookie)}/currency"
        response = new_request(self.cookie, url, {}, "get")
        print(response.json())
        return response.json()["robux"]
    
    def AutoBuy(self, id: int, type: str, amount: int, cooldown_time: int):
        """
        Belirtilen miktar ve zaman aralığıyla otomatik alım yapar.
        """
        for _ in range(amount):
            time.sleep(cooldown_time)
            self.buy(True, id, type)
    
    def BuyEnteredPasses(self, *pass_ids: int):
        """
        Belirtilen gamepassleri satın alır.
        """
        for pass_id in pass_ids:
            try:
                self.buy(True, pass_id, "pass")
            except:
                time.sleep(3)
                self.buy(True, pass_id, "pass")
    
    def donate(self, username, amount):
        """
        Verilen kullanıcıya belirtilen miktarda bağış yapar.
        """
        total_donation = 0
        for gpass in bilgi.get_gamepasses(username):
            if total_donation + gpass[1] <= amount:
                total_donation += gpass[1]
                self.buy(True, gpass[0], "pass")
        
        if total_donation == amount:
            return "success"
        else:
            return f"error: Uygun geçiş(ler) bulunamadı. Atılan: {total_donation}, İstenen: {amount}"

class pass_creator:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def do_offsale(self, passid):
        """
        Belirtilen gamepass  satıştan kaldırır.
        """
        url = f"https://apis.roblox.com/game-passes/v1/game-passes/{passid}/details"
        data = {"IsForSale": False}
        new_request(self.cookie, url, data, "post")
    
    def pass_creator(self, amount):
        """
        Yeni bir gamepass oluşturur ve belirtilen fiyatla satışa çıkarır.
        """
        url = "https://apis.roblox.com/game-passes/v1/game-passes"
        data = {"Name": "thanks :)", "UniverseId": "4783339527"}
        response = new_request(self.cookie, url, data, "post")
        
        try:
            pass_id = response.json()['gamePassId']
            url = f"https://apis.roblox.com/game-passes/v1/game-passes/{pass_id}/details"
            data = {"IsForSale": True, "Price": amount}
            response = new_request(self.cookie, url, data, "post")
            print(response.content)
            return str(pass_id)
        except:
            return "hata"

class Groups:
    def __init__(self, cookie: str, group_id: int):
        self.cookie = cookie
        self.group_id = group_id
    
    def Summary(self, time: str = "day"):
        """
        Grup gelir özetini alır.
        """
        data={}
        url = f"https://economy.roblox.com/v1/groups/{self.group_id}/revenue/summary/{time}"
        response = new_request(self.cookie, url, {}, "get").json()
        data["pendingRobux"]=response["pendingRobux"]
        data["itemSaleRobux"]=response["itemSaleRobux"]
        return data
    def Funds(self):
        """
        Grupta bulunan robux miktarını gösterir
        """
        url = f"https://economy.roblox.com/v1/groups/{self.group_id}/currency"
        response = new_request(self.cookie, url, {}, "get").json()
        return response
    def GiveRank(self,role_id,username):
        """
        belirtilen kullanıcıya belirtilen rolü verir
        """
        url=f"https://groups.roblox.com/v1/groups/{self.group_id}/users/{bilgi.get_user_id_by_username(username)}"
        data={"roleId":role_id}
        response=new_request(self.cookie,url,data,"patch")
        return response.json()
    def Roles(self):
        """
        belirtilen gruptaki rolleri sıralar
        """


