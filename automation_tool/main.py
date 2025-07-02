"""Console entry point for the automation tool."""

import logging
import os
import sys

# Allow running this file directly by adjusting sys.path
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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
    '0': ("5 minutes", 5 * 60),
    '1': ("15 minutes", 15 * 60),
    '2': ("30 minutes", 30 * 60),
    '3': ("45 minutes", 45 * 60),
    '4': ("1 hour", 60 * 60),
    '5': ("1 day", 24 * 60 * 60),
    '6': ("2 days", 2 * 24 * 60 * 60),
    '7': ("1 week", 7 * 24 * 60 * 60),
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
        opts = {}
        idx = 1
        print(f"{idx}. Set Credential"); opts[str(idx)] = 'cred'; idx += 1
        if hasattr(supplier, 'configure_ftp'):
            print(f"{idx}. Set FTP Credentials"); opts[str(idx)] = 'ftpcred'; idx += 1
        if hasattr(supplier, 'configure_location_mapping'):
            print(f"{idx}. Configure Location Mapping"); opts[str(idx)] = 'loc_map'; idx += 1
        if hasattr(supplier, 'configure_sku_mapping'):
            print(f"{idx}. Configure SKU Mapping"); opts[str(idx)] = 'sku_map'; idx += 1
        if isinstance(supplier, CwrSupplier):
            print(f"{idx}. Run Partial Inventory"); opts[str(idx)] = 'inv'; idx += 1
        else:
            print(f"{idx}. Fetch Inventory Update"); opts[str(idx)] = 'inv'; idx += 1
            if hasattr(supplier, 'fetch_inventory_stock'):
                print(f"{idx}. Fetch Inventory Stock Only"); opts[str(idx)] = 'inv_stock'; idx += 1
        if hasattr(supplier, 'fetch_inventory_secondary'):
            print(f"{idx}. Fetch Inventory Update via FTP (Secondary)"); opts[str(idx)] = 'inv_sec'; idx += 1
        if hasattr(supplier, 'fetch_inventory_full'):
            print(f"{idx}. Fetch Full Inventory"); opts[str(idx)] = 'inv_full'; idx += 1
        if hasattr(supplier, 'force_full_sync'):
            print(f"{idx}. Force Full Inventory"); opts[str(idx)] = 'force_full'; idx += 1
        if isinstance(supplier, CwrSupplier):
            print(f"{idx}. Schedule Partial Inventory"); opts[str(idx)] = 'sch_inv'; idx += 1
        else:
            print(f"{idx}. Schedule Inventory Update"); opts[str(idx)] = 'sch_inv'; idx += 1
            if hasattr(supplier, 'fetch_inventory_stock'):
                print(f"{idx}. Schedule Inventory Stock"); opts[str(idx)] = 'sch_inv_stock'; idx += 1
        if hasattr(supplier, 'fetch_inventory_full'):
            print(f"{idx}. Schedule Full Inventory"); opts[str(idx)] = 'sch_inv_full'; idx += 1
        if hasattr(supplier, 'fetch_catalog'):
            print(f"{idx}. Fetch Catalog Now"); opts[str(idx)] = 'cat'; idx += 1
            print(f"{idx}. Schedule Catalog"); opts[str(idx)] = 'sch_cat'; idx += 1
            print(f"{idx}. Manage Catalog"); opts[str(idx)] = 'manage_cat'; idx += 1
        if hasattr(supplier, 'upload_multi_location_inventory'):
            print(f"{idx}. Upload Multi-Location Inventory"); opts[str(idx)] = 'upload_multi'; idx += 1
        if hasattr(supplier, 'test_connection'):
            print(f"{idx}. Test Connection"); opts[str(idx)] = 'test'; idx += 1
        print(f"{idx}. Back"); back_val = str(idx)

        choice = input("Select option: ")
        if choice == back_val:
            break
        action = opts.get(choice)
        if action == 'cred':
            if hasattr(supplier, 'configure_credentials'):
                supplier.configure_credentials()
            else:
                k = input('Credential name: ')
                v = input('Value: ')
                supplier.set_credential(k, v)
                print('Saved.')
        elif action == 'ftpcred':
            if hasattr(supplier, 'configure_ftp'):
                supplier.configure_ftp()
        elif action == 'loc_map':
            if hasattr(supplier, 'configure_location_mapping'):
                supplier.configure_location_mapping()
        elif action == 'sku_map':
            if hasattr(supplier, 'configure_sku_mapping'):
                supplier.configure_sku_mapping()
        elif action == 'inv':
            supplier.fetch_inventory()
        elif action == 'inv_full':
            supplier.fetch_inventory_full()
        elif action == 'force_full':
            if hasattr(supplier, 'force_full_sync'):
                supplier.force_full_sync()
        elif action == 'inv_sec':
            if hasattr(supplier, 'fetch_inventory_secondary'):
                supplier.fetch_inventory_secondary()
        elif action == 'inv_stock':
            if hasattr(supplier, 'fetch_inventory_stock'):
                supplier.fetch_inventory_stock()
        elif action == 'sch_inv':
            print("Select schedule interval:")
            for n, (label, _) in SCHEDULES.items():
                print(f"{n}. {label}")
            opt = input("Choice: ")
            if opt in SCHEDULES:
                schedule_supplier(supplier, SCHEDULES[opt][1])
        elif action == 'sch_inv_full':
            if hasattr(supplier, 'fetch_inventory_full'):
                print("Select schedule interval:")
                for n, (label, _) in SCHEDULES.items():
                    print(f"{n}. {label}")
                opt = input("Choice: ")
                if opt in SCHEDULES:
                    schedule_function(f'{supplier.name}_full', supplier.fetch_inventory_full, SCHEDULES[opt][1], jobs)
        elif action == 'sch_inv_stock':
            if hasattr(supplier, 'fetch_inventory_stock'):
                print("Select schedule interval:")
                for n, (label, _) in SCHEDULES.items():
                    print(f"{n}. {label}")
                opt = input("Choice: ")
                if opt in SCHEDULES:
                    schedule_function(f'{supplier.name}_stock', supplier.fetch_inventory_stock, SCHEDULES[opt][1], jobs)
        elif action == 'cat':
            supplier.fetch_catalog()
        elif action == 'sch_cat':
            print("Select schedule interval:")
            for n, (label, _) in SCHEDULES.items():
                print(f"{n}. {label}")
            opt = input("Choice: ")
            if opt in SCHEDULES:
                schedule_catalog(supplier, SCHEDULES[opt][1])
        elif action == 'manage_cat':
            show_catalog_menu(supplier)
        elif action == 'upload_multi':
            if hasattr(supplier, 'upload_multi_location_inventory'):
                supplier.upload_multi_location_inventory()
        elif action == 'test':
            supplier.test_connection()
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
