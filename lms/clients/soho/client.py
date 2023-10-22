import httpx

from lms.clients.soho.schemas import (
    ClientListSchema,
    HomeworksForReviewSchema,
    ProductListSchema,
)


class SohoClient:
    HOMEWORKS_LIST_URL = (
        "https://api.soholms.com/api/v1/learning/homework/for_review_list"
    )
    CLIENTS_LIST_URL = "https://api.soholms.com/api/v1/client/find_clients"
    PRODUCTS_LIST_URL = "https://api.soholms.com/api/v1/product/list"

    def __init__(self, auth_token: str) -> None:
        self.auth_token = auth_token
        self.headers = {"Authorization": auth_token}

    def get_homeworks_for_reviews_sync(
        self, homework_id: int
    ) -> HomeworksForReviewSchema:
        result = httpx.post(
            url=self.HOMEWORKS_LIST_URL,
            headers=self.headers,
            json={
                "homeworkId": homework_id,
            },
        )
        return HomeworksForReviewSchema(**result.json())

    def get_client_list(self, offset: int = 0, limit: int = 100) -> ClientListSchema:
        result = httpx.post(
            url=self.CLIENTS_LIST_URL,
            headers=self.headers,
            json={
                "limit": limit,
                "offset": offset,
            },
        )
        return ClientListSchema(**result.json())

    def get_product_list(self) -> ProductListSchema:
        result = httpx.post(
            url=self.PRODUCTS_LIST_URL,
            headers=self.headers,
        )
        return ProductListSchema(**result.json())
