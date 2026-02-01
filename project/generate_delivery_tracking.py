import random
import time
import json
from dataclasses import dataclass, asdict
from typing import Optional
import threading
import queue
import argparse

@dataclass
class DeliveryPosition:
    timestamp: int
    driver_id: str
    delivery_id: str
    latitude: float
    longitude: float
    status: str

class DeliveryTrackingGenerator:
    _positions_queue: queue.Queue
    _updates_per_sec: int
    _num_drivers: int
    
    # Starting coordinates for simulation (e.g., São Paulo, Brazil area)
    _LAT_START = -23.5505
    _LON_START = -46.6333
    _COORDINATE_DELTA = 0.001 # Small step for movement

    def __init__(self, updates_per_sec: int = 5, num_drivers: int = 20, max_queue_size: int = 1000):
        self._positions_queue = queue.Queue(maxsize=max_queue_size)
        self._updates_per_sec = updates_per_sec
        self._num_drivers = num_drivers
        
        # Initialize drivers with random positions and statuses
        self._drivers_state = {}
        for i in range(self._num_drivers):
            driver_id = f"driver_{100 + i}"
            self._drivers_state[driver_id] = {
                "delivery_id": f"del_{1000 + i}",
                "lat": self._LAT_START + random.uniform(-0.05, 0.05),
                "lon": self._LON_START + random.uniform(-0.05, 0.05),
                "status": random.choice(["PICKING_UP", "DELIVERING"])
            }

    def _update_driver_position(self, driver_id: str) -> DeliveryPosition:
        state = self._drivers_state[driver_id]
        
        # Simulate movement: add a small random delta to lat/lon
        state["lat"] += random.uniform(-self._COORDINATE_DELTA, self._COORDINATE_DELTA)
        state["lon"] += random.uniform(-self._COORDINATE_DELTA, self._COORDINATE_DELTA)
        
        # Occasionally change status or delivery_id to simulate new deliveries
        if random.random() < 0.01:
            if state["status"] == "DELIVERING":
                state["status"] = "PICKING_UP"
                state["delivery_id"] = f"del_{random.randint(2000, 9999)}"
            else:
                state["status"] = "DELIVERING"

        return DeliveryPosition(
            timestamp=int(time.time()),
            driver_id=driver_id,
            delivery_id=state["delivery_id"],
            latitude=round(state["lat"], 6),
            longitude=round(state["lon"], 6),
            status=state["status"]
        )

    def _tracking_thread(self) -> None:
        delay = 1 / self._updates_per_sec
        driver_ids = list(self._drivers_state.keys())
        
        while True:
            # Pick a random driver to update
            driver_id = random.choice(driver_ids)
            position_update = self._update_driver_position(driver_id)
            self._positions_queue.put(position_update)
            time.sleep(delay)

    def generate_tracking_data(self):
        # Start the background thread for updates
        threading.Thread(target=self._tracking_thread, daemon=True).start()

        while True:
            position = self._positions_queue.get()
            yield position
            self._positions_queue.task_done()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate a delivery tracking stream.')
    parser.add_argument('--drivers', type=int, default=10, help='Number of drivers to simulate (default: 10)')
    parser.add_argument('--updates', type=float, default=5.0, help='Updates per second (default: 5.0)')
    
    args = parser.parse_args()

    # Simulate a delivery tracking stream
    tracking_gen = DeliveryTrackingGenerator(updates_per_sec=args.updates, num_drivers=args.drivers)
    count = 0
    print(f"Starting Delivery Tracking Simulation for {args.drivers} drivers at {args.updates} updates/sec... (Press Ctrl+C to stop)")
    try:
        for pos in tracking_gen.generate_tracking_data():
            count += 1
            pos_dict = asdict(pos)
            print(json.dumps(pos_dict))
    except KeyboardInterrupt:
        print(f"\nSimulation stopped. {count} tracking updates generated.")
