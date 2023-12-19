import requests


class UserRequests:
    def __init__(self) -> None:
        self.URL = 'http://localhost:8080/users/'

    async def requests_post_user_data(self, user_id: int):
        requests.post(
            url=self.URL + 'registration',
            params={'user_id': user_id}
        )
