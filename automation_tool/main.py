import logging
import os
"""Console entry point for the automation tool."""

from automation_tool.suppliers import (
    KeystoneSupplier,
    CwrSupplier,
    SeawideSupplier,
)
from automation_tool.scheduler import RepeatedTimer

logging.basicConfig(
    filename='automation.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

SUPPLIERS = {
    '1': KeystoneSupplier(),
    '2': CwrSupplier(),
    '3': SeawideSupplier(),
}

SCHEDULES = {
    '1': 300,
    '2': 900,
    '3': 1200,
    '4': 1800,
    '5': 2700,
    '6': 3600,
    '7': 86400,
    '8': 604800,
}

jobs = {}

def schedule_supplier(supplier, interval):
    if supplier.name in jobs:
        jobs[supplier.name].stop()
    timer = RepeatedTimer(interval, supplier.fetch_inventory)
    timer.start()
    jobs[supplier.name] = timer
    logging.info("Scheduled %s every %s seconds", supplier.name, interval)


def show_supplier_menu(key):
    supplier = SUPPLIERS[key]
    while True:
        print(f"\nSupplier: {supplier.name}")
        print("1. Set Credential")
        print("2. Fetch Inventory Now")
        print("3. Schedule Inventory")
        print("4. Back")
        choice = input("Select option: ")
        if choice == '1':
            k = input("Credential name: ")
            v = input("Value: ")
            supplier.set_credential(k, v)
            print("Saved.")
        elif choice == '2':
            supplier.fetch_inventory()
        elif choice == '3':
            print("Select schedule interval:")
            for n, sec in SCHEDULES.items():
                print(f"{n}. {sec} seconds")
            opt = input("Choice: ")
            if opt in SCHEDULES:
                schedule_supplier(supplier, SCHEDULES[opt])
        elif choice == '4':
            break
        else:
            print("Invalid option")


def main():
    while True:
        print("\nAutomation Tool")
        print("1. Keystone Automotive")
        print("2. CWR Distribution")
        print("3. Seawide")
        print("4. Quit")
        choice = input("Select supplier: ")
        if choice in SUPPLIERS:
            show_supplier_menu(choice)
        elif choice == '4':
            for t in jobs.values():
                t.stop()
            break
        else:
            print("Invalid option")

if __name__ == '__main__':
    main()
