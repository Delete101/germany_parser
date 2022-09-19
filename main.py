import os.path
import socket
import time
import external_webdriver
import telebot
import sqlite3
from selenium.webdriver.common.by import By
from anticaptchaofficial.imagecaptcha import *
from telebot import types
from datetime import datetime
from sqlite3 import Error

# Import --------------------------------------

try:
    driver = external_webdriver.getdriver()
except Exception as ex:
    print(f'{ex}')


# WebDriver Settings ---------------------------------

# connection func
def create_connection(path):
    connection_ = None
    try:
        connection_ = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
        return connection_
    except Error as ex:
        print(f"The create_connection '{ex}' occurred")


connection = create_connection(os.path.abspath('base/base.sqlite'))


# Connect to DataBase ------------------------------------


# Create DataBase --------------------------------------

# create_seats_table = """
# CREATE TABLE seats (
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# date_time TEXT,
# status TEXT
# );
# """
#
# execute_query(connection, create_seats_table)

# Create DataBase -----------------------------------------


# add to database
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as ex:
        print(f"The execute_query '{ex}' occurred")


# get database result
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The execute_read_query '{e}' occurred")


# Print Base --------------------

# select_seats = """SELECT *
# from seats
# ORDER BY id DESC
# """
# seats = execute_read_query(connection, select_seats)
# # print DataBase to user
# counter = 0
# for seat in seats:
#     print(seat)

# Print Base -------------------

# Data Base ---------------------------------------------------

exceptions = 0


# get captcha
def capctha_screen():
    global exceptions
    captcha_body = driver.find_element(By.ID, 'global')
    if 'Введите код с картинки' in captcha_body.text:
        try:
            find_captcha = driver.find_element(By.TAG_NAME, 'captcha')
            find_captcha.screenshot('captcha.png')
        except Exception as ex:
            exceptions += 1
            print('Captcha not found')


def input_captcha():
    global exceptions
    exceptions = 0
    try:
        # captcha_text_ = input()
        captcha_text_ = external_webdriver.solvecaptcha()
        flag = True
        while flag:
            if len(captcha_text_) == 6:
                flag = False
            else:
                print('Длина должна быть 6 символов \n')
                replace_button = driver.find_element(By.XPATH,
                                                     '/html/body/div[1]/div[2]/div[1]/div[1]/form/div[1]/div/input')
                replace_button.click()
                time.sleep(3)
                capctha_screen()
                captcha_text_ = external_webdriver.solvecaptcha()
        time.sleep(2)
        input_captcha = driver.find_element(By.NAME, 'captchaText')
        time.sleep(2)
        input_captcha.send_keys(captcha_text_)
        time.sleep(2)
        go_to_date_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/form/div[3]/input[1]')
        go_to_date_button.click()
    except Exception as ex:
        exceptions += 1
        print(f'Error {ex}')

    time.sleep(3)
    try:
        flag = True
        while flag:
            time.sleep(2)
            incorrect_pass = driver.find_elements(By.TAG_NAME, 'div')
            i = 2
            for text in incorrect_pass:
                if 'неверно' in text.text:
                    print(f"Попытка ввода N {i} \n")
                    capctha_screen()
                    captcha_text_ = external_webdriver.solvecaptcha()
                    time.sleep(2)
                    input_captcha = driver.find_element(By.NAME, 'captchaText')
                    input_captcha.send_keys(captcha_text_)
                    go_to_date_button = driver.find_element(By.XPATH,
                                                            '/html/body/div[1]/div[2]/div[1]/div[1]/form/div[3]/input[1]')
                    go_to_date_button.click()
                    time.sleep(1)
                else:
                    flag = False
            flag = False
    except Exception as ex:
        exceptions += 1
        print(f'Captcha send error \n')


def check_seats():
    global dt_string, status, seats_, exceptions
    seats_ = False
    try:
        div_text = driver.find_element(By.XPATH, '/html/body/div')
        # check to seats
        if 'введите код с картинки' in div_text.text.lower():
            capctha_screen()
            input_captcha()
        h2_text = driver.find_elements(By.CSS_SELECTOR, 'h2')
        for text in h2_text:
            try:
                # check date
                # check seats
                if 'свободных мест нет' in text.text:
                    dt = datetime.now()
                    dt_string = dt.strftime("%d-%m-%Y %H:%M:%S")
                    status = False
                    # save info to base
                    add_info = f"""
                    INSERT INTO 
                        seats (date_time, status)
                    VALUES
                        ('{dt_string}', '{status}')
                    """
                    execute_query(connection, add_info)
                    print('Свободных мест нет, попробуйте позже')
                    time.sleep(2)
                    arrow_right = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[1]/h2[2]/a[2]')
                    arrow_right.click()
                    time.sleep(2)
                    seats_ = False
                    break
                check_seats = driver.find_element(By.TAG_NAME, 'body')
                if 'запись на прием' in check_seats.text.lower():
                    print('Места найдены')
                    seats_ = True
                    break
            except Exception as ex:
                exceptions += 1
                print(f'Error {ex} \n')

        if seats_:
            page_source = driver.page_source.encode('utf-8')
            dt = datetime.now()
            dt_string = dt.strftime("%d_%m_%Y__%H_%M_%S")
            with open(f'html_pages/{dt_string}.html', 'xb') as f:
                f.write(page_source)
            body_screen = driver.find_element(By.TAG_NAME, 'html')
            img = body_screen.screenshot('seats.png')
            dt_string = dt.strftime("%d-%m-%Y %H:%M:%S")
            status = 'True'
            # save info to base
            add_info = f"""
            INSERT INTO 
                seats (date_time, status)
            VALUES
                ({dt_string}, {status});
            """
            execute_query(connection, add_info)
    except Error as ex:
        exceptions += 1
        print(f'Base {ex} error \n')


# main func
def find_seats():
    # get main url
    global exceptions
    main_url = 'https://service2.diplo.de/rktermin/extern/choose_realmList.do?locationCode=mins&request_locale=ru'
    driver.get(main_url)
    try:
        category_button = driver.find_element(By.CLASS_NAME, 'arrow')
        url_1 = category_button.get_attribute('href')
        driver.get(url_1)
    except Exception as ex:
        exceptions += 1
        print('First page not found/Button not found \n')
        driver.refresh()

    # First Page ------------------------------------------

    try:
        buttons_to_short_visa = driver.find_elements(By.CLASS_NAME, 'arrow')
        url_2 = buttons_to_short_visa[1].get_attribute('href')
        driver.get(url_2)
    except Exception as ex:
        exceptions += 1
        print('Second page not found/Button not found \n')

    # Second Page ----------------------------------------------

    try:
        buttons_to_captcha = driver.find_elements(By.CLASS_NAME, 'arrow')
        url_3 = buttons_to_captcha[1].get_attribute('href')
        driver.get(url_3)
    except Exception as ex:
        exceptions += 1
        print('Button to captcha not found \n')

    # Page with link to captcha -----------------------------------

    capctha_screen()

    # Captcha Screen ------------------------------------

    # input captcha
    input_captcha()

    for _ in range(4):
        check_seats()

    # Send Captcha ----------------------------------------------


# Try to find seats ----------------------------------------------


# bot token
def check_pc():
    global TOKEN
    if socket.gethostname().lower() == 'hp-envy':
        TOKEN = '5459404746:AAFyegBvrNZbPOLnxSircuFWM2GmCLFpcbc'
    elif socket.gethostname().lower() == 'prodesk':
        TOKEN = '5343646851:AAF3oCtTa5pjRnKrGqzvuUNMMzM7ng97abo'
    return TOKEN


# TeleBot

bot = telebot.TeleBot(check_pc())

try:
    # start message
    # @bot.message_handler(content_types=['text'])
    # def get_start_message(message):
    #     if message.text == "/start":
    # keyboard = types.InlineKeyboardMarkup(row_width=2)
    # key_yes = types.InlineKeyboardButton(text='Да✌', callback_data='yes')
    # key_base_in_chat = types.InlineKeyboardButton(text='База в чат📄', callback_data='base_chat')
    # key_base_txt = types.InlineKeyboardButton(text='База в txt ✉', callback_data='base_txt')
    # key_no = types.InlineKeyboardButton(text='Стоп😑', callback_data='/stop')
    # keyboard.add(key_yes, key_no, key_base_in_chat, key_base_txt)
    # bot.send_message(message.from_user.id, text='Подписаться на обновления?', reply_markup=keyboard)

    # # check answer
    # @bot.callback_query_handler(func=lambda call: True)
    # def callback_worker(call):
    #     if call.data == "yes":

    # start message
    @bot.message_handler(content_types=['text'])
    def get_start_message(message):
        if message.text == "/start":
            flag = True
            counter = 0
            exceptions = 0
            # main func
            find_seats()
            while flag:
                counter += 1
                print(f'Круг # {counter} пройден... \n \n')
                if counter % 5 == 0:
                    bot.send_message(chat_id=-1001700105127, text=f'Попыток {counter}, ошибок {exceptions}')
                try:
                    time.sleep(600)
                    # dt = datetime.now()
                    # dt_string = dt.strftime("%d-%m-%Y | %H:%M:%S")
                    # bot.send_message(chat_id=-1001700105127, text=f'База на {dt_string} 🙈')
                    select_seats = """SELECT * 
                       from seats
                       ORDER BY id DESC
                       """
                    seats = execute_read_query(connection, select_seats)
                    # print DataBase to user
                    for seat in seats:
                        str_seat = " ".join(map(str, seat))
                        split_str = str_seat.split()
                        try:
                            if str(split_str[3]) == 'True':
                                img = open('seats.png', 'rb')
                                bot.send_photo(chat_id=-1001700105127, photo=img)
                                print('Скрин отправлен')
                                os.remove(os.path.abspath('seats.png'))
                        except Exception as ex:
                            print('IMG not found')
                            continue
                    driver.refresh()
                    time.sleep(2)
                    div_text = driver.find_element(By.XPATH, '/html/body/div')
                    # check to seats
                    if 'свободных мест нет' in div_text.text.lower():
                        h2_text = driver.find_elements(By.CSS_SELECTOR, 'h2')
                        for text in h2_text:
                            if '11/2022' in text.text.lower():
                                for _ in range(3):
                                    time.sleep(2)
                                    arrow_right = driver.find_element(By.XPATH,
                                                                      '/html/body/div[1]/div[2]/div[1]/div[1]/h2[2]/a[1]')
                                    arrow_right.click()
                                print('Возврат курсора')
                        for i in range(3):
                            check_seats()

                    div_text = driver.find_element(By.XPATH, '/html/body/div')
                    # check to seats
                    if 'введите код с картинки' in div_text.text.lower():
                        capctha_screen()
                        input_captcha()
                        check_seats()
                except Exception as ex:
                    print(f'Error {ex} \n')
                    exceptions += 1
                    time.sleep(20)
                    continue

        # elif call.data == "base_chat":
        #     try:
        #         dt = datetime.now()
        #         dt_string = dt.strftime("%d-%m-%Y | %H:%M:%S")
        #         bot.send_message(call.message.chat.id, f'База на {dt_string} 🙈')
        #         select_seats = """SELECT *
        #            from seats
        #            ORDER BY id DESC
        #            """
        #         seats = execute_read_query(connection, select_seats)
        #         # print DataBase to user
        #         counter = 0
        #         for seat in seats:
        #             if counter <= 30:
        #                 str_seat = " ".join(map(str, seat))
        #                 split_str = str_seat.split()
        #                 if str(split_str[3]) != 'False':
        #                     bot.send_message(call.message.chat.id, f'ID: {split_str[0]} | Date: {split_str[1]} | Time: {split_str[2]} | Status: {split_str[3]}')
        #                     counter += 1
        #             else:
        #                 break
        #     except Exception as ex:
        #         print('Base error')
        #
        # elif call.data == 'base_txt':
        #     try:
        #         select_seats = """
        #         SELECT *
        #         from seats
        #         ORDER BY id DESC
        #         """
        #         seats = execute_read_query(connection, select_seats)
        #         with open('base/base.txt', 'w+') as f:
        #             for seat in seats:
        #                 str_seat = " ".join(map(str, seat))
        #                 split_str = str_seat.split()
        #                 for elem in split_str:
        #                     f.write(elem + ' ')
        #                 f.write('\n')
        #             print('Base.txt created')
        #         dt = datetime.now()
        #         dt_string = dt.strftime("%d-%m-%Y | %H:%M:%S")
        #         bot.send_message(call.message.chat.id, f'База на {dt_string} 🙈')
        #         bot.send_document(call.message.chat.id, open('base/base.txt', 'r', encoding='utf-8'))
        #
        #     except Exception as ex:
        #         print('Base.txt error')
        #
        # elif call.data == "/stop":
        #     bot.send_message(call.message.chat.id, 'Stopping...🛑')
        #     driver.close()
        #     bot.stop_polling()
        #     flag = False


    bot.polling(non_stop=True)

except Exception as ex:
    print(f'Telebot {ex} error\n')

# Telebot ---------------------------------------------------
