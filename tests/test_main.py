import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from storage import events

from aiokafka import AIOKafkaProducer
import asyncio
import json
from asgi_lifespan import LifespanManager


@pytest.fixture(autouse=True)
def clear_events():
    events.clear()
    yield
    events.clear()


@pytest.fixture()
def add_events():
    events.appendleft({'id': 'e8684120-9ef1-4dc4-abf0-fcac2ea77ad3', 'schema': 'public',
                       'table': 'discounts_app_city', 'action': 'UPDATE', 'data': {'id': 3, 'name': 'Сочи4'},
                       'dataOld': {'id': 3, 'name': 'Сочи5'}, 'commitTime': '2025-05-29T16:05:22.628585Z'})
    events.appendleft({'id': 'f41263e3-c1ad-4a23-8c4d-28dbe0d0ca26', 'schema': 'public',
                       'table': 'discounts_app_discountcategory', 'action': 'UPDATE',
                       'data': {'id': 2, 'image': 'category_images/e25d7c0afe0382eb5098cb0e74d90400_Nm3N8PB.png',
                                'name': 'Доставка еды и продукты'},
                       'dataOld': {'id': 2, 'image': 'category_images/e25d7c0afe0382eb5098cb0e74d90400_Nm3N8PB.png',
                                   'name': 'Доставка еды и продукты2'}, 'commitTime': '2025-05-29T16:05:14.325814Z'})


@pytest.mark.asyncio
async def test_get_event_list_events(add_events):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200

        content = response.text
        assert "discounts_app_city" in content
        assert "discounts_app_discountcategory" in content
        assert "Сочи4" in content


@pytest.mark.asyncio
async def test_get_event_filtered_city(add_events):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/", params={"selected": "city"})
    assert response.status_code == 200

    content = response.text
    assert "discounts_app_city" in content
    assert "discounts_app_discountcategory" not in content


@pytest.mark.asyncio
async def test_get_event_filtered_category(add_events):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/", params={"selected": "category"})
    assert response.status_code == 200

    content = response.text
    assert "discounts_app_city" not in content
    assert "discounts_app_discountcategory" in content


@pytest.mark.asyncio
async def test_get_event_filtered_discount(add_events):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/", params={"selected": "discount"})
    assert response.status_code == 200

    content = response.text
    assert "discounts_app_city" not in content
    assert "discounts_app_discountcategory" not in content


@pytest.mark.asyncio
async def test_get_event_filtered_company(add_events):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/", params={"selected": "company"})
    assert response.status_code == 200

    content = response.text
    assert "discounts_app_city" not in content
    assert "discounts_app_discountcategory" not in content


# # # # #
# kafka #
# # # # #


@pytest.mark.asyncio
async def test_kafka():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            producer = AIOKafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await producer.start()
            try:
                await producer.send_and_wait("wal_listener.wal_city",
                                             {'id': 'test_id', 'schema': 'public',
                                              'table': 'discounts_app_city', 'action': 'UPDATE',
                                              'data': {'id': 3, 'name': 'Test_city_2'},
                                              'dataOld': {'id': 3, 'name': 'Test_city_1'},
                                              'commitTime': '2025-05-29T16:05:22.628585Z'})
            finally:
                await producer.stop()

            for _ in range(15):
                await asyncio.sleep(0.5)
                response = await ac.get("/")
                if "Test_city_1" in response.text:
                    break

            assert response.status_code == 200
            assert "Test_city_1" in response.text
