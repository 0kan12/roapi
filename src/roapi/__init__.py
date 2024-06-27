import requests
import time

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
AUTH_URL = 'https://auth.roblox.com/v2/logout'

class RobloxRequest:
    def __init__(self, cookie: str, url: str, data=None, method="get"):
        self.cookie = cookie
        self.url = url
        self.data = data
        self.method = method
        self.session = requests.Session()
        self.response = None
        self.send_request()
    
    def send_request(self):
        """
        Sends HTTP request.
        """
        try:
            request_func = getattr(self.session, self.method.lower())
            headers = self.get_headers()
            cookies = self.get_cookies()
            self.response = request_func(self.url, data=self.data, headers=headers, cookies=cookies)
            self.response.raise_for_status()  # Raise error for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
    
    def get_headers(self):
        """
        Returns HTTP headers.
        """
        token = self.session.post(AUTH_URL, headers={'User-Agent': USER_AGENT}, cookies=self.get_cookies()).headers.get('x-csrf-token', '')
        return {"X-CSRF-TOKEN": token} if token else {}
    
    def get_cookies(self):
        """
        Returns HTTP cookies.
        """
        return {".ROBLOSECURITY": self.cookie}
    
    def get_json(self):
        """
        Converts response to JSON format.
        """
        if self.response:
            return self.response.json()
        else:
            return None

class AssetManager:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def delete_asset(self, asset_id):
        """
        Deletes an asset from Roblox inventory.
        """
        url = f"https://www.roblox.com/asset/delete-from-inventory"
        data = {"assetId": asset_id}
        RobloxRequest(self.cookie, url, data, "post")
        print("Item deleted")
    
    def revoke_game_pass(self, pass_id):
        """
        Revokes a Roblox game pass.
        """
        url = f"https://www.roblox.com/game-pass/revoke"
        data = {"id": pass_id}
        RobloxRequest(self.cookie, url, data, "post")

class RobloxInfo:
    @staticmethod
    def get_user_id(cookie):
        """
        Returns the Roblox ID of the user logged in with the given cookie.
        """
        url = "https://users.roblox.com/v1/users/authenticated"
        response = RobloxRequest(cookie, url, {}, "get")
        return response.get_json()['id']

    @staticmethod
    def get_info_request_url(type: str, id: int):
        """
        Generates the info request URL for a specific asset or pass.
        """
        if type == "pass":
            return f"https://apis.roblox.com/game-passes/v1/game-passes/{id}/product-info"
        elif type == "asset":
            return f"https://economy.roblox.com/v2/assets/{id}/details"

    @staticmethod
    def get_info(id: int, type: str):
        """
        Retrieves information for the specified ID and type (ProductId, Creator Id, PriceInRobux).
        """
        url = RobloxInfo.get_info_request_url(type, id)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [data['ProductId'], data['Creator']['Id'], data['PriceInRobux']]

    @staticmethod
    def get_user_id_by_username(username):
        """
        Returns the Roblox ID of the user with the given username.
        """
        API_ENDPOINT = "https://users.roblox.com/v1/usernames/users"
        payload = {'usernames': [username]}
        response = requests.post(API_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()['data'][0]['id']
    
    @staticmethod
    def get_gamepasses(username):
        """
        Lists game passes for the given user.
        """
        user_id = RobloxInfo.get_user_id_by_username(username)
        url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=Public&limit=50"
        response = requests.get(url)
        response.raise_for_status()
        ids = [game['id'] for game in response.json()['data']]
        
        gamepasses = []
        for universe_id in ids:
            url = f'https://games.roblox.com/v1/games/{universe_id}/game-passes?limit=100&sortOrder=Asc'
            response = requests.get(url)
            response.raise_for_status()
            for gamepass in response.json()['data']:
                if gamepass['price'] is not None:
                    gamepasses.append([gamepass['id'], gamepass['price']])
        
        return gamepasses

class Buyer:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def buy(self, delete_after_purchase: bool, id: int, type: str):
        """
        Buys the specified asset or pass.
        """
        info = RobloxInfo.get_info(id, type)
        data = {"expectedCurrency": 1, "expectedPrice": info[2], "expectedSellerId": info[1]}
        url = f"https://economy.roblox.com/v1/purchases/products/{info[0]}"
        response = RobloxRequest(self.cookie, url, data, "post")
        print(response.get_json())
        
        if delete_after_purchase:
            if type == "pass":
                AssetManager(self.cookie).revoke_game_pass(id)
            elif type == "asset":
                AssetManager(self.cookie).delete_asset(id)
    
    def get_robux_amount(self):
        """
        Returns the user's Robux amount.
        """
        url = f"https://economy.roblox.com/v1/users/{RobloxInfo.get_user_id(self.cookie)}/currency"
        response = RobloxRequest(self.cookie, url, {}, "get")
        print(response.get_json())
        return response.get_json()["robux"]
    
    def autobuy(self, id: int, type: str, amount: int, cooldown_time: int):
        """
        Automatically buys with the specified amount and cooldown time.
        """
        for _ in range(amount):
            time.sleep(cooldown_time)
            self.buy(True, id, type)
    
    def buy_entered_passes(self, *pass_ids: int):
        """
        Buys the specified game passes.
        """
        for pass_id in pass_ids:
            try:
                self.buy(True, pass_id, "pass")
            except:
                time.sleep(3)
                self.buy(True, pass_id, "pass")
    
    def donate(self, username, amount):
        """
        Donates the specified amount to the given user.
        """
        total_donation = 0
        for gpass in RobloxInfo.get_gamepasses(username):
            if total_donation + gpass[1] <= amount:
                total_donation += gpass[1]
                self.buy(True, gpass[0], "pass")
        
        if total_donation == amount:
            return "success"
        else:
            return f"error: Suitable passes not found. Given: {total_donation}, Required: {amount}"

class GamePassCreator:
    def __init__(self, cookie: str):
        self.cookie = cookie
    
    def take_off_sale(self, pass_id):
        """
        Takes the specified game pass off sale.
        """
        url = f"https://apis.roblox.com/game-passes/v1/game-passes/{pass_id}/details"
        data = {"IsForSale": False}
        RobloxRequest(self.cookie, url, data, "post")
    
    def create_pass(self, amount):
        """
        Creates a new game pass and puts it on sale with the specified price.
        """
        url = "https://apis.roblox.com/game-passes/v1/game-passes"
        data = {"Name": "Thanks :)", "UniverseId": "4783339527"}
        response = RobloxRequest(self.cookie, url, data, "post")
        
        try:
            pass_id = response.get_json()['gamePassId']
            url = f"https://apis.roblox.com/game-passes/v1/game-passes/{pass_id}/details"
            data = {"IsForSale": True, "Price": amount}
            response = RobloxRequest(self.cookie, url, data, "post")
            print(response.get_json())
            return str(pass_id)
        except:
            return "error"

class RobloxGroups:
    def __init__(self, cookie: str, group_id: int):
        self.cookie = cookie
        self.group_id = group_id
    
    def revenue_summary(self, time: str = "day"):
        """
        Retrieves group revenue summary.
        """
        url = f"https://economy.roblox.com/v1/groups/{self.group_id}/revenue/summary/{time}"
        response = RobloxRequest(self.cookie, url).get_json()
        return response
    
    def give_rank(self, role_id, username):
        """
        Gives the specified role to the specified user.
        """
        url = f"https://groups.roblox.com/v1/groups/{self.group_id}/users/{RobloxInfo.get_user_id_by_username(username)}"
        data = {"roleId": role_id}
        response = RobloxRequest(self.cookie, url, data, "post")
        return response.get_json()
    
    def list_roles(self):
        """
        Lists roles in the group.
        """
        url = f"https://groups.roblox.com/v1/groups/{self.group_id}/roles"
        response = RobloxRequest(self.cookie, url).get_json()
        return response['roles']
