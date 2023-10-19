from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class HomeworkSchema(BaseModel):
    client_homework_id: int = Field(alias="clientHomeworkId")
    client_id: int = Field(alias="clientId")
    sent_to_review_at: datetime = Field(alias="sentToReviewAt")
    chat_url: HttpUrl = Field(alias="chatUrl")
    vk_id: int = Field(alias="vkId")


class HomeworksForReviewSchema(BaseModel):
    homeworks: list[HomeworkSchema]


class ClientSchema(BaseModel):
    id: int
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName", default="")
    emails: list[str]


class ClientListSchema(BaseModel):
    clients: list[ClientSchema]
    limit: int
    offset: int


class PaymentSchema(BaseModel):
    id: int
    name: str
    percent: int


class ProductSchema(BaseModel):
    id: int = Field(alias="productId")
    flow_id: int | None = Field(alias="flowId", default=None)
    name: str
    payment_schemas: list[PaymentSchema] = Field(alias="paymentSchemas")


class ProductListSchema(BaseModel):
    products: ProductSchema
