# Queue management functions (add and call queues).
import pet_manager
import json

queue: list[tuple[int, str, str, str]] = []
queue_number: int = 0
queue_lock: bool = False
last_called: tuple[int, str, str, str] | None = None

def add_queue(pet_id: str):
  global queue_number
  global queue_lock

  if queue_lock:
    print("Queue is locked, Cannot add another queue.")
    return

  pet = pet_manager.load_pet()

  if pet_id not in pet or not pet[pet_id] or not pet[pet_id]["Name"] or not pet[pet_id]["Owner"]:
    print("No pet data!")
    return

  queue_number += 1
  queue.append((queue_number, pet_id, pet[pet_id]["Name"], pet[pet_id]["Owner"]))
  print(f"Queue: {queue_number} is already added.")

def call_queue():
  global last_called
  if queue:
    last_called = queue.pop(0)
    queue_id, pet_id, petname, owner = last_called
    print(f"Calling queue {queue_id} : Pet ID : {pet_id} : Pet name : {petname} (Own by : {owner}).")
  else:
    print("No more queue in line.")

def view_queue():
  if queue:
    print("\n(------------------ Queue ------------------)")
    for queue_id, pet_id, petname, owner in queue:
      print(f"Queue {queue_id}: Pet ID : {pet_id} : {petname}(Own by : {owner}).")
  else:
    print("Queue is empty.")

def reset_queue():
  global queue_number
  global last_called
  queue.clear()
  queue_number = 0
  last_called = None
  print("Queue now reset!")

def queue_status():
  if last_called:
    queue_id, pet_id, petname, owner = last_called
    print(f"Latest called queue: {queue_id} : Pet ID : {pet_id} : {petname} (Own by : {owner}).")
  else:
    print("Latest called queue: None")
  print(f"All remaining queues: {len(queue)}")
  view_queue()