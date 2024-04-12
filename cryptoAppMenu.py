import threading
import time
import tkinter as tk
import datetime
from threading import Thread
from playwright.sync_api import sync_playwright
#
#
# initializes sets
crypto_name = ''
enable_bot = False
crypto_inventory = 0
buy_price = 0
sell_price = 0
#
#
# collects crypto prices
def spider_prices():
    global price_label, run_threads, total_amount, clock, crypto_name, buy_price, sell_price
    if crypto_name != '':
        print(f'Seeking the cryptocurrency: {crypto_name.upper()}')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(f'https://coinmarketcap.com/currencies/{crypto_name}')
                print('1')
                price_element = page.wait_for_selector('#section-coin-overview > div.sc-f70bb44c-0.flfGQp.flexStart.alignBaseline > span')
                print('2')
                stop_button.config(state=tk.NORMAL)
                print('3')
                bot_button.config(state=tk.NORMAL)
                print('4')
            except:
                print('ERROR: Couldn\'t find server')
                price_label.config(text='ERROR: Couldn\'t reach server')
                yes_button.config(state=tk.NORMAL)
                no_button.config(state=tk.NORMAL)
                quit_button.config(state=tk.NORMAL)
                run_threads = False
            previous_price = None
            previous_clock = None
            while run_threads:
                price = price_element.text_content()
                clock = datetime.datetime.now().strftime('%I:%M %p')
                precise_clock = datetime.datetime.now().strftime('%I:%M:%S %p')
                if price != previous_price:
                    price_label.config(text=f'{clock} - {crypto_name.upper()} Price: {price}')
                    if previous_price != None:
                        aged_price_label.config(fg='gray', text=f'{previous_clock} - {crypto_name.upper()} Price: {previous_price}', font=('helvetica', 8))
                    print(f'{precise_clock} - Current {crypto_name} price: {price}')
                    previous_price = price
                    previous_clock = clock
                    buy_price = -(float(price.replace('$', '').replace(',', '')))
                    sell_price = float(price.replace('$', '').replace(',', ''))
            context.close()
            browser.close()
            print('Closing spider thread..')
    else:
        crypto_name = 'bitcoin'
        spider_prices()
#
#
# buy / sell functions
def buy_sell():
    price_label.config(text=f'Prices for {crypto_name.upper()} are updating...')
    buy_button.config(text='Buy')
    sell_button.config(text='Sell')
    buy_button.config(state=tk.DISABLED)
    sell_button.config(state=tk.DISABLED)
    while buy_price == 0:
        if run_threads == False:
            break
    while run_threads:
        if buy_entry.get() == '':
            buy_button.config(state=tk.DISABLED)
        elif buy_entry.get() != '':
            try:
                buy_totals = (int(buy_entry.get()) * buy_price) + total_amount
                if buy_totals >= 0:
                    buy_button.config(state=tk.NORMAL, command=buy_method)
                else:
                    buy_button.config(state=tk.DISABLED)
            except:
                buy_button.config(state=tk.DISABLED)
        else:
            buy_button.config(state=tk.DISABLED)
        if sell_entry.get() == '':
            sell_button.config(state=tk.DISABLED)
        elif crypto_inventory > 0 and sell_entry.get() != '':
            try:
                sell_totals = int(sell_entry.get()) * sell_price - total_amount
                if sell_totals >= 0:
                    sell_button.config(state=tk.NORMAL, command=sell_method)
                else:
                    sell_button.config(state=tk.DISABLED)
            except:
                sell_button.config(state=tk.DISABLED)
        else:
            sell_button.config(state=tk.DISABLED)
    print('Closing finance thread..')
def buy_method():
    global total_amount, crypto_inventory
    crypto_increase = int(buy_entry.get())
    total_amount += buy_price * crypto_increase
    crypto_inventory += crypto_increase
    update_totals()
    bought_label.config(fg='gray', text=f'{clock} - Bought {crypto_name.upper()} at ${sell_price}')
    buy_entry.delete(0, tk.END)
    buy_button.config(state=tk.DISABLED)
def sell_method():
    global total_amount, crypto_inventory
    crypto_decrease = int(sell_entry.get())
    total_amount += sell_price * crypto_decrease
    crypto_inventory -= crypto_decrease
    update_totals()
    sold_label.config(fg='gray', text=f'{clock} - Sold {crypto_name.upper()} at ${sell_price}')
    sell_entry.delete(0, tk.END)
    sell_button.config(state=tk.DISABLED)
#
#
# thread management
def thread_management():
    global run_threads
    run_threads = True
    yes_button.config(state=tk.DISABLED)
    no_button.config(state=tk.DISABLED)
    stop_button.config(text='End Tasks', state=tk.DISABLED)
    quit_button.config(state=tk.DISABLED)
    spider_thread = Thread(target=spider_prices)
    app_thread = Thread(target=buy_sell)
    spider_thread.start()
    app_thread.start()
    total_threads()
def total_threads():
    global thread_count
    active_threads = threading.enumerate()
    thread_count = len(active_threads)
    print(f'Number of threads running: {thread_count}')
def stop_threads():
    global run_threads, crypto_name
    run_threads = False
    crypto_name = ''
    yes_button.config(state=tk.NORMAL)
    no_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    quit_button.config(state=tk.NORMAL)
def quit_app():
    total_threads()
    app.quit()
    print('\nClosed application.')
#
#
# popup menu
def close_popup(event=None):
    global crypto_name
    crypto_name = crypto_entry.get()
    yes_button.config(state=tk.DISABLED)
    no_button.config(state=tk.DISABLED)
    thread_management()
    popup.destroy()
def popup_menu():
    global popup, crypto_entry
    popup = tk.Toplevel(app)
    popup.title('Popup')
    cInfo_label = tk.Label(popup, text='Type the cryptocurrency in the box below.')
    cInfo_label.pack(padx=5, pady=5)
    crypto_entry = tk.Entry(popup, width=6)
    crypto_entry.pack(pady=5)
    crypto_entry.focus_set()
    crypto_entry.bind("<Return>", close_popup)
#
#
# bot popup menu
def activate_bot():
    global enable_bot, bot_config
    while sell_price == 0:
        pass
    enable_bot = True
    bot_config = tk.Toplevel(app)
    bot_config.title('Activating Bot')
    bInfo_label = tk.Label(bot_config, text='DISCLAIMER: this bot is designed to\n'
                                            'use the maximum amount of the\n'
                                            'budget (that you have deposited\n'
                                            'into this application) in attempts\n'
                                            'to make the highest possible\n'
                                            'profit. If you understand and\n'
                                            'agree to let the bot make trades\n'
                                            'on your behalf then go ahead and\n'
                                            'create price-points at which your\n'
                                            'bot will buy and sell at. When\n'
                                            'you\'re ready click \'Run Now\'\n')
    bInfo_label.pack(padx=20, pady=2)
    buyPricepoint_label = tk.Label(bot_config, text='Buy rate:')
    buyPricepoint_label.pack(pady=2)
    def enable_button():
        global threshold_lower, threshold_higher
        if buyPricepoint_entry.get() and sellPricepoint_entry.get():
            run_button.config(state=tk.NORMAL, command=bonus_thread)
            threshold_lower = float(buyPricepoint_entry.get())
            threshold_higher = float(sellPricepoint_entry.get())
        else:
            run_button.config(state=tk.DISABLED)
    buyPricepoint_entry = tk.Entry(bot_config, width=6)
    buyPricepoint_entry.pack(pady=2)
    sellPricepoint_label = tk.Label(bot_config, text='Sell rate:')
    sellPricepoint_label.pack(pady=2)
    sellPricepoint_entry = tk.Entry(bot_config, width=6)
    sellPricepoint_entry.pack(pady=2)
    run_button = tk.Button(bot_config, text='Run Now', state=tk.DISABLED)
    run_button.pack(pady=20)
    buyPricepoint_entry.bind("<KeyRelease>", lambda event: enable_button())
    sellPricepoint_entry.bind("<KeyRelease>", lambda event: enable_button())
def deactivate_bot():
    global enable_bot
    enable_bot = False
    print('Closing Bot thread..')
    bot_button.config(text='Activate Bot', command=activate_bot)
def bonus_thread():
    bot_config.destroy()
    bot_button.config(text='Deactivate Bot', command=deactivate_bot)
    if enable_bot == True:
        bot_thread = Thread(target=bot_functions)
        bot_thread.start()
    else:
        print('ERROR: Bot could not be started.')
#
#
# bot official functions
def bot_functions():
    global enable_bot
    total_threads()
    while enable_bot == True:
        affordable = int(total_amount / sell_price)
        if affordable > 0 and crypto_inventory == 0:
            if threshold_lower >= sell_price:
                buy_entry.insert(0, str(affordable))
                time.sleep(0.5)
                buy_button.invoke()
                print(f'Purchased {affordable} {crypto_name.upper()}')
        if crypto_inventory > 0 and sell_price >= threshold_higher:
            sell_entry.insert(0, str(crypto_inventory))
            time.sleep(0.5)
            sell_button.invoke()
            print(f'Sold all {crypto_name.upper()}')
#
#
# collects input from the app
def update_totals():
    total_label.config(text=f'Tradable Allowance: ${total_amount}')
    crypto_label.config(text=f'You have a total of {crypto_inventory} {crypto_name.upper()}')
def deposit_money(event):
    global total_amount
    if event.keysym == 'Return':
        amount = deposit_entry.get()
        try:
            amount = float(amount)
            total_amount += amount
            update_totals()
            if amount > 0:
                print(f'Deposited: {amount}')
                history_label.config(fg='gray', text=f'Deposited ${amount}')
            elif amount == 0:
                print('Nothing happened')
            else:
                print(f'Withdrawn: {amount}')
                history_label.config(fg='gray', text=f'Withdrawn ${abs(amount)}')
        except ValueError:
            print('Invalid input. Please enter a valid number.')
        deposit_entry.delete(0, tk.END)
    else:
        deposit_entry.config(fg='black')
#
#
# the app menu
app = tk.Tk()
app.title('Trading Simulator')
app.geometry('300x600')
app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)
app.columnconfigure(2, weight=1)
info_label = tk.Label(app, text='Current Version 1.0\n\nThis is an intelligent\ncrypto trader application.')
info_label.grid(row=0, column=1, pady=10)
fade_text = 'Type in a dollar amount'
initialize = '0'
deposit_entry = tk.Entry(app, fg='gray', width=21)
deposit_entry.insert(0, fade_text)
deposit_entry.bind("<FocusIn>", lambda event: deposit_entry.delete(0, tk.END))
deposit_entry.bind("<Key>", deposit_money)
deposit_entry.grid(row=1, column=1, pady=5)
total_amount = 0
total_label = tk.Label(app, text=f'Tradeable Allowance: ${total_amount:.2f}')
total_label.grid(row=2, column=1, pady=10)
history_label = tk.Label(app, text='')
history_label.grid(row=3, column=1)
crQuestion_label = tk.Label(app, text='Do you have a specific cryptocurrency\nin mind that you\'d like to trade?')
crQuestion_label.grid(row=4, column=1, pady=5)
yes_button = tk.Button(app, text='Yes', command=popup_menu)
yes_button.grid(row=5, column=1, pady=1)
no_button = tk.Button(app, text='No, choose for me', command=thread_management)
no_button.grid(row=6, column=1, pady=1)
crypto_label = tk.Label(app, text='')
crypto_label.grid(row=7, column=1, pady=5)
buy_entry = tk.Entry(app, width=6)
buy_entry.grid(row=8, column= 1, pady=1)
buy_button = tk.Button(app, text='')
buy_button.grid(row=9, column=1, pady=1)
bought_label = tk.Label(app, text='')
bought_label.grid(row=10, column=1, pady=1)
sell_entry = tk.Entry(app, width=6)
sell_entry.grid(row=11, column= 1, pady=1)
sell_button = tk.Button(app, text='')
sell_button.grid(row=12, column=1, pady=1)
sold_label = tk.Label(app, text='')
sold_label.grid(row=13, column=1, pady=1)
price_label = tk.Label(app, text='')
price_label.grid(row=14, column=1, pady=1)
aged_price_label = tk.Label(app, text='')
aged_price_label.grid(row=15, column=1, pady=1)
stop_button = tk.Button(app, text='', state=tk.DISABLED, command=stop_threads)
stop_button.grid(row=16, column=1, pady=1)
quit_button = tk.Button(app, text='Quit', command=quit_app)
quit_button.grid(row=17, column=1, pady=1)
bot_button = tk.Button(app, text='Activate Bot', state=tk.DISABLED, command=activate_bot)
bot_button.grid(row=18, column=1, pady=1)
app.mainloop()