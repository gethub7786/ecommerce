import logging
import os
"""Console entry point for the automation tool."""

from automation_tool import (
    KeystoneSupplier,
    CwrSupplier,
    SeawideSupplier,
)
from automation_tool.scheduler import RepeatedTimer
from automation_tool import catalog

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

# Available schedule intervals (label, seconds)
SCHEDULES = {
    '1': ("5 minutes", 5 * 60),
    '2': ("1 hour", 60 * 60),
    '3': ("1 day", 24 * 60 * 60),
    '4': ("1 week", 7 * 24 * 60 * 60),
}

catalog_jobs = {}

jobs = {}

def schedule_function(name, func, interval, store):
    if name in store:
        store[name].stop()
    timer = RepeatedTimer(interval, func)
    timer.start()
    store[name] = timer
    logging.info("Scheduled %s every %s seconds", name, interval)

def schedule_supplier(supplier, interval):
    schedule_function(supplier.name, supplier.fetch_inventory, interval, jobs)

def schedule_catalog(supplier, interval):
    if hasattr(supplier, 'fetch_catalog'):
        schedule_function(f'{supplier.name}_catalog', supplier.fetch_catalog, interval, catalog_jobs)

def show_catalog_menu(supplier):
    name = supplier.name
    while True:
        rows = catalog.load_rows(name)
        print(f"\nCatalog for {name} - {len(rows)} rows")
        print("1. Delete SKU")
        print("2. Delete via File")
        print("3. Back")
        choice = input("Select option: ")
        if choice == '1':
            sku = input('SKU to delete: ')
            catalog.delete_sku(name, sku)
            print('Deleted', sku)
        elif choice == '2':
            path = input('Delete file path: ')
            catalog.delete_from_file(name, path)
            print('Processed delete file')
        elif choice == '3':
            break
        else:
            print('Invalid option')


def show_supplier_menu(key):
    supplier = SUPPLIERS[key]
    while True:
        print(f"\nSupplier: {supplier.name}")
        print("1. Set Credential")
        print("2. Fetch Inventory Now")
        print("3. Schedule Inventory")
        if hasattr(supplier, 'fetch_catalog'):
            print("4. Fetch Catalog Now")
            print("5. Schedule Catalog")
            print("6. Manage Catalog")
        if hasattr(supplier, 'test_connection'):
            print("7. Test Connection")
            back_opt = '8'
        else:
            back_opt = '4' if not hasattr(supplier, 'fetch_catalog') else '7'
        print(f"{back_opt}. Back")
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
            for n, (label, _) in SCHEDULES.items():
                print(f"{n}. {label}")
            opt = input("Choice: ")
            if opt in SCHEDULES:
                schedule_supplier(supplier, SCHEDULES[opt][1])
        elif hasattr(supplier, 'fetch_catalog') and choice == '4':
            supplier.fetch_catalog()
        elif hasattr(supplier, 'fetch_catalog') and choice == '5':
            print("Select schedule interval:")
            for n, (label, _) in SCHEDULES.items():
                print(f"{n}. {label}")
            opt = input("Choice: ")
            if opt in SCHEDULES:
                schedule_catalog(supplier, SCHEDULES[opt][1])
        elif hasattr(supplier, 'fetch_catalog') and choice == '6':
            show_catalog_menu(supplier)
        elif hasattr(supplier, 'test_connection') and choice == '7':
            supplier.test_connection()
        elif choice == back_opt:
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
            for t in list(jobs.values()) + list(catalog_jobs.values()):
                t.stop()
            break
        else:
            print("Invalid option")

if __name__ == '__main__':
    main()
