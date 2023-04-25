import os
import time
import pytz
import json
import random
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

get_india_datetime = lambda: (datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S'), datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y'))

class Database:
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['g_creds'])
    creds = creds = Credentials.from_service_account_info(info=creds_json, scopes=scope)
    transaction_id_generator = lambda : f"{int(time.time())}-{random.randint(1, 100000)}"

    @staticmethod
    def date_validator(input_date):
        try:
            print("Date validation Function On Force")
            df  = Database.get_sales_data()
            sale_dates = pd.to_datetime(df['sale_date'],format='%d-%m-%Y',errors='coerce')
            input_date = pd.to_datetime(input_date,format='%d-%m-%Y',errors='coerce')
            if pd.Timestamp(input_date) in sale_dates.values:
                return True
            else:
                return False
        except Exception as e:
            print("An error occurred: ", e)
            return None

    @staticmethod
    def sheets_data_updater(dictionary, sheet_name, sheet_number, task, required_data = False):
        try:
            client = gspread.authorize(Database.creds)
            sheet = client.open(sheet_name).worksheet(sheet_number)
            if task == 'Updating_sales_data':
                dictionary['transaction_id'] = Database.transaction_id_generator()
                sheet.append_row(list(dictionary.values()))
                print("Data appended to sheets!")
                return True
            elif task ==  "Updating_stock_Finance":
                labels = ['available_stock', 'available_empties', 'available_amount', 'On_hold_amount', 'e_commerce', 'Total_Expensives']
                values = [dictionary[label] for label in labels]
                sheet.update('A2:F2', [values])
                print("Stock and finance data updated in Google Sheets DB")
                return True
            elif task ==  "Updating_transaction_record":
                sheet.append_row(list(dictionary.values()))
                print("Updating_transaction_record")
                return True
            elif task == 'STOCK_IMPORTED':
                if required_data:
                    information = {}
                    information['transaction_id'] = Database.transaction_id_generator()
                    sheet.update('A2', dictionary.get('available_stock'))
                    sheet.update('B2', dictionary.get('available_empties'))
                    print("As STOCK_IMPORTED, Data updated in DB for stock and empties")
                    new_data = Database.get_sheet_data()
                    information['reason'] = 'STOCK_IMPORTED'
                    Database.create_update_json(required_data, new_data, information)
                    return True
        except Exception as e:
            print(f"An error occurred while updating data: {e}")
            return False

    @staticmethod
    def get_sheet_data():
        try:
            sheet = gspread.authorize(Database.creds).open('sale_logger').worksheet('Sheet3')
            labels = ['available_stock', 'available_empties', 'available_amount', 'On_hold_amount', 'e_commerce', 'Total_Expensives']
            data = {label: int(sheet.cell(2, index + 1).value) for index, label in enumerate(labels)}
            return data
        except Exception as e:
            print(f"An error occurred while fetching sheet data: {e}")
            return None
            
    @staticmethod       
    def get_sales_data(twosheet=False):
        try:
            if twosheet:
                sale_logger = gspread.authorize(Database.creds).open('sale_logger').worksheet('Sheet2').get_all_values()
                stock_finance = gspread.authorize(Database.creds).open('sale_logger').worksheet('Sheet3')
                labels = ['available_stock', 'available_empties', 'available_amount', 'On_hold_amount', 'e_commerce', 'Total_Expensives']
                data =  {label: int(stock_finance.cell(2, index + 1).value) for index, label in enumerate(labels)}
                print("Page Viewed!")
                return pd.DataFrame(sale_logger[1:], columns=sale_logger[0]), data
            else:
                worksheet = gspread.authorize(Database.creds).open('sale_logger').worksheet('Sheet2')
                data = worksheet.get_all_values()
                df = pd.DataFrame(data[1:], columns=data[0])
            return df
        except gspread.exceptions.APIError as e:
            print(f"An API error occurred: {e}")
            return e
        except Exception as e:
            print(f"An error occurred: {e}")
            return e

    @staticmethod
    def data_calculator(information):
        try:
            required_data = Database.get_sheet_data()
            # Calculate new values
            available_stock = required_data['available_stock'] - int(information["total_cans"])
            available_empties = required_data['available_empties'] + int(information["total_cans"]) - int(information["online_deposites"]) + int(information["retail_deposites"])
            available_amount = required_data['available_amount'] + int(information["final_payment"])
            On_hold_amount = required_data['On_hold_amount'] + int(information["On_hold_amount"]) - int(information["received_on_hold_amount"])
            e_commerce = required_data['e_commerce'] + int(information["E-commerce_amount"])
            Total_Expensives = required_data['Total_Expensives'] +  int(information["expenses"])
    
            updated_data = {
                'available_stock': available_stock,
                'available_empties': available_empties,
                'available_amount': available_amount,
                'On_hold_amount': On_hold_amount,
                'e_commerce': e_commerce,
                'Total_Expensives': Total_Expensives}
            information['reason']="sales_data_updated"
            Database.create_update_json(required_data, updated_data, information)
            checker = Database.sheets_data_updater(updated_data, 'sale_logger', 'Sheet3','Updating_stock_Finance')
            if checker == True:
                print("Updating Google Sheet DB...")
                return True
            else:
                return checker
        except Exception as e:
            print("Error in data calculation: ", e)

    @staticmethod
    def create_update_json(old_data, new_data, information):
        try:
            print("Transaction creating")
            update_dict = {key: {'old_value': old_data.get(key), 'new_value': new_data.get(key, {})} for key in new_data}
            my_dict = {f"{k}_{change_type}_value": v.get(change_type+'_value', '') for k, v in update_dict.items() for change_type in ['old', 'new']}
            my_dict.update(transaction_id=information['transaction_id'], reason = information['reason'], time=get_india_datetime()[0], date=get_india_datetime()[1])
            Database.sheets_data_updater(my_dict, 'sale_logger', 'Sheet4', 'Updating_transaction_record')
        except Exception as e:
            print(f"Error occurred while creating or updating JSON: {e}")
        else:
            print("Transaction created and updated successfully!")

    @staticmethod
    def stock_finance_handler(dictionary):
        if dictionary.get('reason') == 'STOCK_IMPORTED':
            required_data = Database.get_sheet_data()
            new_dict = {
                'available_stock': required_data.get('available_stock', 0) + int(dictionary.get("stock", 0)),
                'available_empties': required_data.get('available_empties', 0) - int(dictionary.get("empties", 0)) + int(dictionary.get("deposit", 0)),
                'p_deposites': int(dictionary.get("deposit", 0)),}
            checker = Database.sheets_data_updater(new_dict, 'sale_logger', 'Sheet3', 'STOCK_IMPORTED',required_data)
            if checker == True:
                return True
            else:
                return False
        elif dictionary.get('reason') == 'not':
            print("else two ") 
            return False