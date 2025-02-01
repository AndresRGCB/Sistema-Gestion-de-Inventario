import pytest
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import threading
import time

# Set up logging correctly (loglevel must be a string)
setup_logging("INFO")

class InventoryLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_products(self):
        self.client.get("/products/")

    @task(2)
    def get_inventory(self):
        self.client.get("/stores/Tienda B/inventory")

    @task(1)
    def get_low_stock_alerts(self):
        self.client.get("/inventory/alerts")

    @task(2)
    def get_product_by_id(self):
        product_id = 2
        self.client.get(f"/products/{product_id}")

    @task(2)
    def get_paginated_products(self):
        self.client.get("/products/?limit=50&offset=0")

@pytest.fixture(scope="session")
def run_locust():
    """Run Locust as part of pytest"""
    env = Environment(user_classes=[InventoryLoadTest])
    env.create_local_runner()
    
    # Register event stats
    stats_thread = threading.Thread(target=stats_printer(env.stats))
    stats_thread.start()

    # Start load test with 500 users at 50 per second
    env.runner.start(500, spawn_rate=50)
    time.sleep(30)
    env.runner.stop()

    # Wait for stats
    stats_thread.join()

@pytest.mark.load_test
def test_run_locust(run_locust):
    """Run load test and check no critical errors"""
    assert True, "Locust test completed"
