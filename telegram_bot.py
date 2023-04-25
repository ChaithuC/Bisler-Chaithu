import os
import pytz
import telebot
from datetime import datetime
from data_handlers import Database


get_india_datetime = lambda: (datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S'), datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y'))

class BotGadu:
    def __init__(self):
        self.bot = telebot.TeleBot(os.environ['token'])
        print(f"Bot on Work at time , Date are > {get_india_datetime()}")
        
        @self.bot.message_handler(commands=['start'])
        def start(message):
            print(f"Bot working for user First name: {message.from_user.first_name} Last name: {message.from_user.last_name} and ID : {message.chat.id}")
            user_input = self.bot.reply_to(message, "Hello Amigo! Please Enter Your Password to Continue ")
            self.bot.register_next_step_handler(user_input, self.authorize_user)

    def authorize_user(self, user_input):
        input = int(user_input.text) 
        if input == int(os.environ['sales_enter_password']): 
            self.bot.send_message(user_input.chat.id,"Entered into the sales data entry Mode")
            date = self.bot.send_message(user_input.chat.id,"Please Enter the Date of sales in this format: dd-mm-yyyy (e.g. 02-06-2004)")
            self.bot.register_next_step_handler(date, self.get_date)
        elif input == int(os.environ['Authoriser']):
            self.bot.send_message(user_input.chat.id,"Entered into Authoriser Mode")
            self.bot.send_message(user_input.chat.id,"To Update stock Reply 1")
            output = self.bot.send_message(user_input.chat.id,"To Finance Reply 2")
            self.bot.register_next_step_handler(output, self.S_F_Handler)
            return
        else:
            self.bot.send_message(user_input.chat.id, "Hey man, This is else block")
    
    def get_date(self, user_input):
        entered_date = user_input.text
        sale_date = datetime.strptime(entered_date, "%d-%m-%Y").date()
        sales_data = {'sale_date': sale_date.strftime("%d-%m-%Y")}
        sale_checker = Database.date_validator(sales_data.get('sale_date', {}))
        if sale_checker == True:
            self.bot.send_message(user_input.chat.id, f"Data for the Date :{sales_data.get('sale_date', {})} is already existed")
            self.bot.send_message(user_input.chat.id, "Click /start to restart and Try Again")
        elif sale_checker == False:
            off_cans = self.bot.send_message(user_input.chat.id, f"Enter Retails sales for can(s) on {sales_data.get('sale_date', {})}")
            self.bot.register_next_step_handler(off_cans, self.get_retail_sales, sales_data)
        else:
            self.bot.send_message(user_input.chat.id, f"Hey man there is an issue with the DB. Error is {sale_checker}")
        return 
            
    def get_retail_sales(self, user_input, sales_data):
        try:
            retail_can_sales = int(user_input.text)
        except ValueError:
            self.bot.send_message(user_input.chat.id, "Invalid input, please enter a numerical value for Online can(s) sales, Please /start again here.")
        sales_data['retail_can_sales'] = retail_can_sales
        try:
            online_cans = self.bot.send_message(user_input.chat.id, f" Enter Online Can(s) sales on {sales_data.get('sale_date', {})}")
            self.bot.register_next_step_handler(online_cans, self.get_online_sales, sales_data)
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error: {e} occurred while sending the message for online sales. Please /start again here.")
        return 
    
    def get_online_sales(self, user_input, sales_data):
        try:
            online_can_sales = int(user_input.text)
        except ValueError:
            self.bot.send_message(user_input.chat.id, "Invalid input, please enter a numerical value for Online can(s) sales, Please /start again here.")
        sales_data['online_can_sales'] = online_can_sales
        try:
            whole_sale_cans = self.bot.send_message(user_input.chat.id, f" Enter Wholesale Can(s) sales on {sales_data.get('sale_date', {})}")
            self.bot.register_next_step_handler(whole_sale_cans, self.get_whole_sales, sales_data)
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
    
    def get_whole_sales(self, user_input, sales_data):
        try:
            wholesale_can_sales = user_input.text
            if wholesale_can_sales.isnumeric():
                sales_data['wholesale_can_sales'] = wholesale_can_sales
                online_cans_deposite = self.bot.send_message(user_input.chat.id,f"Enter the Online Can(s) Deposite count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(online_cans_deposite, self.get_online_deposite, sales_data)   
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
                
    def get_online_deposite(self, user_input, sales_data):
        try:
            online_deposites = user_input.text
            if online_deposites.isnumeric():
                sales_data['online_deposites'] = online_deposites
                offline_can_deposite = self.bot.send_message(user_input.chat.id,f"Please Enter Retail can(s) deposite on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(offline_can_deposite, self.get_retail_deposite, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")

        
        return
    
    def get_retail_deposite(self, user_input, sales_data):
        try:
            retail_deposites = user_input.text
            if retail_deposites.isnumeric():
                sales_data['retail_deposites'] = retail_deposites
                whole_sale_deposite = self.bot.send_message(user_input.chat.id,f"Enter the Whole sale can(s) deposite count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(whole_sale_deposite, self.get_wholesale_deposite, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
    
    def get_wholesale_deposite(self, user_input, sales_data):
        try:
            wholesale_deposite = user_input.text
            if wholesale_deposite.isnumeric():
                sales_data['wholesale_deposite'] = wholesale_deposite
                leakagee = self.bot.send_message(user_input.chat.id, f"Enter leakage count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(leakagee, self.get_leakage, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
    
    def get_leakage(self, user_input, sales_data):
        try:
            leakage = user_input.text
            if leakage.isnumeric():
                sales_data['leakage'] = leakage
                complimentry_cans = self.bot.send_message(user_input.chat.id,f"Enter the complementry can(s) on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(complimentry_cans, self.sale_confirmation, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return        
                
    def sale_confirmation(self, user_input, sales_data):
        try:
            complimentry_cans = user_input.text
            if complimentry_cans.isnumeric():
                sales_data['complimentry_cans'] = complimentry_cans
                sales_data['total_cans'] = int(sales_data['retail_can_sales']) + int(sales_data['online_can_sales']) + int(sales_data['wholesale_can_sales']) + int(sales_data['complimentry_cans'])
                confirm_total_cans = self.bot.send_message(user_input.chat.id, f"Please confirm that {sales_data['total_cans']} can(s) delivered on {sales_data.get('sale_date', {})} including complementry cans {sales_data.get('complimentry_cans', {})} by pressing Yes")
                self.bot.register_next_step_handler(confirm_total_cans, self.confirm_calculator, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
            
    def confirm_calculator(self, user_input, sales_data):
        confirm  = user_input.text
        if confirm.lower() == 'yes':
            try:
                sales_data['retail_can_sales_amount'] = (int(sales_data['retail_can_sales']) * 90)
                sales_data['retail_deposite_amount'] = (int(sales_data['retail_deposites']) * 150)
                sales_data['whole_sale_amount'] = (int(sales_data['wholesale_can_sales']) * 75)
                sales_data['whole_sale_deposite_amount'] = (int(sales_data['wholesale_deposite']) * 150)
                sales_data['E-commerce_amount'] = (int(sales_data['online_can_sales']) * 90 +
                                           int(sales_data['online_deposites']) * 150 +
                                           int(sales_data['leakage']) * 61)
                sales_data['calculated_received_amount'] = sales_data.get('retail_can_sales_amount', {}) + sales_data.get('whole_sale_amount', {}) + sales_data.get('retail_deposite_amount', {})+ sales_data.get('whole_sale_deposite_amount', {})
                amount = self.bot.send_message(user_input.chat.id, (f"Please confirm the Retail Deposit is {sales_data.get('retail_deposite_amount', {})}, Whole sale Deposit is {sales_data.get('whole_sale_deposite_amount', {})} and Online deposit cans  {sales_data['online_deposites'] } press yes to confirm and move into next"))
                self.bot.register_next_step_handler(amount, self.payments_on_hold, sales_data)
            except Exception as e:
                self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        else:
            self.bot.send_message(user_input.chat.id, 'Invalid input, Click /start to restart')
        return
              
    def payments_on_hold(self, user_input, sales_data):
        try:
        	if user_input.text.lower() == "yes":
        		payment_hold = self.bot.send_message(user_input.chat.id,f"Please enter the total payment on hold on {sales_data['sale_date']}")
        		self.bot.register_next_step_handler(payment_hold, self.on_hold_payments_recieved, sales_data)
        	else:
        		self.bot.send_message(user_input.chat.id,"Got into wrong step Click here to restart /start")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
            
    def on_hold_payments_recieved(self, user_input, sales_data):
        try:
            hold_payment = user_input.text
            sales_data["On_hold_amount"] = hold_payment
            on_hold_payment_received = self.bot.send_message(user_input.chat.id, "Enter the on-hold payments received from previous orders")
            self.bot.register_next_step_handler(on_hold_payment_received, self.get_expenses, sales_data)
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occured")
            
    def get_expenses(self, user_input, sales_data):
        try:
            received_on_hold_amount = int(user_input.text)
            sales_data['received_on_hold_amount'] = received_on_hold_amount
            expenses = self.bot.send_message(user_input.chat.id, f"Enter the total Expensives on {sales_data['sale_date']}")
            self.bot.register_next_step_handler(expenses, self.get_received_on_hold_amount, sales_data)
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occured")
        return
    
    def get_received_on_hold_amount(self, user_input, sales_data):
        try:
            sales_data['expenses'] = int(user_input.text)
            sales_data['final_payment'] = (int(sales_data['calculated_received_amount']) + int(sales_data['received_on_hold_amount'])) - (int(sales_data['On_hold_amount']) + int(sales_data['expenses']))
            final_view = self.bot.send_message(user_input.chat.id, f"Confirm that total amount received for sale is {sales_data.get('final_payment', {})} and On hold payments received is {sales_data.get('received_on_hold_amount', {})} and expensives for today = {sales_data['expenses']}. Press Yes to confirm and complete updating")
            self.bot.register_next_step_handler(final_view, self.complete_print, sales_data)
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occurred")
    
    def complete_print(self, user_input, sales_data):
        try:
            input_text = user_input.text.lower()
            if input_text == "yes":
                message_text = ""
                for item, key in sales_data.items():
                    message_text += f'{item} : {key}\n'
                self.bot.send_message(user_input.chat.id, message_text)
                self.bot.send_message(user_input.chat.id,"Data updating in the Back-End! please wait for the confirmation")
                db_update_confirmation = Database.sheets_data_updater(sales_data,'sale_logger', 'Sheet2', 'Updating_sales_data')
                if db_update_confirmation == True:
                    self.bot.send_message(user_input.chat.id, "Sales Data updated Sucessfully, Now Stock and Finance Data is Updating ")
                    f_s_updater = Database.data_calculator(sales_data)
                    if f_s_updater == True:
                        self.bot.send_message(user_input.chat.id, "Stock and Finance Data Updated Sucessfully. Bye - Bye ")
                    else:
                        self.bot.send_message(user_input.chat.id, f"Error Ocured while Updating the stock and finance and the error is : > {f_s_updater}.")       
                    return 
                else:
                    self.bot.send_message(user_input.chat.id, f"Data Unable to Update Sucessfully due to this error {db_update_confirmation}.")      
            else:
                self.bot.send_message(user_input.chat.id, "Data updating failed. Please try again by pressing /start.")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error {e} occurred while processing your request.Please try again by pressing /start.")

    def S_F_Handler(self, user_input):
        if int(user_input.text) == 1:
            self.bot.send_message(user_input.chat.id, "stock updating mode\n Enter the STOCK Imported")
            self.bot.register_next_step_handler(user_input, self.handle_stock_input)
        elif int(user_input.text) == 2:
            self.bot.send_message(user_input.chat.id, "Finance updating mod\n Enter amount to deduct from available amount")
            self.bot.register_next_step_handler(user_input, self.update_available_amount)
        else:
            self.bot.send_message(user_input.chat.id, "Came to an exception")
        return
    
    def handle_stock_input(self, user_input):
        stock = int(user_input.text)
        self.bot.send_message(user_input.chat.id, "how many EMPTIES are returned")
        self.bot.register_next_step_handler(user_input, self.handle_empties_input, stock)
    
    def handle_empties_input(self, user_input, stock):
        empties = int(user_input.text)
        self.bot.send_message(user_input.chat.id, "How many cans of DEPOSIT")
        self.bot.register_next_step_handler(user_input, self.handle_deposit_input, stock, empties)
        
    def handle_deposit_input(self, user_input, stock, empties):
        deposit = int(user_input.text)
        data = {'stock': stock, 'empties': empties, 'deposit': deposit, 'reason': "STOCK_IMPORTED",}
        message = f"Data collected:\nStock: {data['stock']}\nEmpties: {data['empties']}\nDeposit: {data['deposit']}\nReason: {data['reason']}\n\n Please wait while data being updating in the background"
        self.bot.send_message(user_input.chat.id, message)
        confirmation = Database.stock_finance_handler(data)
        if confirmation == True:
            self.bot.send_message(user_input.chat.id, "Data Updated Sucessfully!")
            self.bot.send_message(user_input.chat.id, "Press here > /start to restart ")
        else:
            self.bot.send_message(user_input.chat.id, "There is an issue in updating the data")

    
    ## Test Mode   
    def update_available_amount(self, user_input):
        available_amount  = int(user_input.text)
        data = {'available_amount': available_amount}
        self.bot.send_message(user_input.chat.id, "Enter the E-Commerece Amount received")
        self.bot.register_next_step_handler(user_input, self.update_ecommerce_amount, data)
        return 

    def update_ecommerce_amount(self, user_input, data):
        data['e_commerce'] = int(user_input.text)
        self.bot.send_message(user_input.chat.id, "Enter amount to deducte from on hold amount")
        self.bot.register_next_step_handler(user_input, self.update_hold_amount, data)
        return 
    
    def update_hold_amount(self, user_input, data):
        data['hold_amount'] =  int(user_input.text)
        self.bot.send_message(user_input.chat.id,"Enter amount to deducte from Expenses ")
        self.bot.register_next_step_handler(user_input, self.reason, data)
        return 
        
    def reason(self, user_input, data):
        data['update_expenses'] = int(user_input.text)
        self.bot.send_message(user_input.chat.id,"Enter the Reson for upadates ")
        self.bot.register_next_step_handler(user_input, self.update_expenses, data)
        return 
    
    def update_expenses(self, user_input, data):
        data['reason'] =  user_input.text
        self.bot.send_message(user_input.chat.id, f"Updating with: {data}")
        confirmation = Database.stock_finance_handler(data)
        if confirmation == True:
            print("yes")
        else:
            self.bot.send_message(user_input.chat.id, "There is an issue in updating the data")
        return  
    ## END 

    def run(self):
        self.bot.infinity_polling()