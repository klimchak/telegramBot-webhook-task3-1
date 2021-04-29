import logging
import sys
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from bot.settings import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)
from email_validator import validate_email, EmailNotValidError          # библиотека валидации имейла
from bot.keyboard import kbStart, inlineKbAfterLogin, inlineKbAfterSetNewCard, inlineKbAnsSetCardOrNot
from aiogram.types import ReplyKeyboardRemove
from bot.sffunc import auth, getBalance, setNewExpCard, getLatestExpCard    # sf function                                                
import datetime
from bot.telegramcalendar import create_calendar                            # для календаря

current_shown_dates={}
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# cmessage == 0 - старт и просьба входа. будет требовать логин
# cmessage == 1 - будет требовать пароль
# cmessage == 2 - действия для админа
# cmessage == 3 - действия для пользователя
# cmessage == 4 - 2 шаг при добавлении карты
# cmessage == 5 - 3 шаг при добавлении карты

cmessage = 0
def cmessageUp (count):
    global cmessage
    cmessage = count

emailinquery = ''
def setEmail (dataInEmail):
    global emailinquery
    emailinquery = dataInEmail
def getEmail ():
    global emailinquery
    return emailinquery

idContact = ''
def setIdContact (dataInContact):
    global idContact
    idContact = dataInContact
def getIdContact ():
    global idContact
    return idContact

dateExpCard = ''
def setDateExpCard (dataDateExpCard):
    global dateExpCard
    dateExpCard = dataDateExpCard
def getDateExpCard ():
    global dateExpCard
    return dateExpCard

descrExpCard = ''
def setDescrExpCard (dataDescrExpCard):
    global descrExpCard
    descrExpCard = dataDescrExpCard
def getDescrExpCard ():
    global descrExpCard
    return descrExpCard

currExpCard = ''
def setCurrExpCard (dataCurrExpCard):
    global currExpCard
    currExpCard = dataCurrExpCard
def getCurrExpCard ():
    global currExpCard
    return currExpCard

botLatestMessageId = 0
def setBotLatestMessageId (dataBotLatestMessageId):
    global botLatestMessageId
    botLatestMessageId = dataBotLatestMessageId
def getBotLatestMessageId ():
    global botLatestMessageId
    return botLatestMessageId

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    cmessageUp(0)
    for i in range(2):
        if i == 1:
            await bot.delete_message(message.chat.id, message.message_id)
        if i == 0: 
            messs = await bot.send_message(message.chat.id, "Введите логин", reply_markup=ReplyKeyboardRemove())
            setBotLatestMessageId(messs.message_id)

@dp.callback_query_handler()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    code = callback_query.data[4:]
    if code == 'balance':
        idUser = getIdContact()
        reminder = getBalance(idUser)
        await bot.answer_callback_query(
            callback_query.id,
            text='Ваш баланс составляет: ' + str(reminder) + '$', show_alert=True)
    
    if code == 'setnewcard':
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id)
            if i == 2:
                messs = await bot.send_message(callback_query.from_user.id, 'На какой день желаете создать карточку?', reply_markup=inlineKbAfterSetNewCard)
                setBotLatestMessageId(messs.message_id)
            if i == 0:
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
    
    if code == 'backtomain':
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id, 'Понял. Возвращаемся назад 😒')
            if i == 2:
                messs = await bot.send_message(callback_query.from_user.id, 'Какую операцию желаете выполнить?', reply_markup=inlineKbAfterLogin)
                setBotLatestMessageId(messs.message_id)
            if i == 0:  
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
    
    if code == 'setdatetoday':
        nowDate = datetime.datetime.now()
        nowDateStr = str(nowDate.year) + '-' + str(nowDate.month) + '-' + str(nowDate.day)
        setDateExpCard(nowDateStr)
        cmessageUp(4)
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id)
            if i == 2:
                messs = await bot.send_message(callback_query.from_user.id, "Создаем карту на дату: " + nowDateStr + "\nВведите описание траты.")
                setBotLatestMessageId(messs.message_id)
            if i == 0:  
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
    
    if code == 'setthisexpcard':
        result = setNewExpCard(getIdContact(), getDateExpCard(), getCurrExpCard(), getDescrExpCard())
        if result == True:
            cmessageUp(3)
            for i in range(4):
                if i == 1:
                    await bot.answer_callback_query(callback_query.id)
                if i == 2:
                    await bot.send_message(callback_query.from_user.id, "Усешно! Новая карточка расходов добавлена.\nДанные карточки:" + '\n- дата карточки: ' + getDateExpCard() + '\n- сумма: ' + getCurrExpCard()  + '\n- описание траты: ' + getDescrExpCard())
                if i == 3:
                    mess = await bot.send_message(callback_query.from_user.id, 'Ваши дальнейшие действия? ', reply_markup=inlineKbAfterLogin)
                    setBotLatestMessageId(mess.message_id)                
                if i == 0:  
                    await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
        else:
            cmessageUp(3)
            await bot.answer_callback_query(callback_query.id, "Возникла ошибка! Попробуйте еще раз или обратитесь к администратору.", show_alert=True)

    if code == 'exit':
        print('\n        Успешный выход пользователя: ' + '\n        '+ str(callback_query.from_user.first_name) + '\n        ' + str(callback_query.from_user.last_name) + '\n        ' + str(callback_query.from_user.username))
        sys.stdout.flush()
        cmessageUp(0)
        setCurrExpCard('')
        setDateExpCard('')
        setDescrExpCard('')
        setEmail('')
        setIdContact('')
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id)
            if i == 2:
                await bot.send_message(callback_query.from_user.id, 'Вы вышли из приложения Expense App.\nДля входа нажмите /start и введите Email и пароль.', reply_markup=kbStart)        
            if i == 0:  
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
        
    if code == 'help':
        helpText = 'Взаимодействие с ботом осуществляется посредством кнопок.\nДля выполнения необходимых действий следуйте подсказкам.\np.s. это первый бот и первый опыт программирования на Python'
        await bot.answer_callback_query(callback_query.id, helpText, show_alert=True)

    if code == 'opencalendar':
        now = datetime.datetime.now()
        chat_id = callback_query.from_user.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(now.year, now.month)
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id)
            if i == 2:
                messs = await bot.send_message(callback_query.from_user.id, "На какой день желаете создать карточку?", reply_markup=markup)
                setBotLatestMessageId(messs.message_id)
            if i == 0:  
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
       
    if 'DAY' in callback_query.data[0:13]:
        chat_id = callback_query.from_user.id
        saved_date = current_shown_dates.get(chat_id)
        last_sep = callback_query.data.rfind(';') + 1
        if saved_date is not None:
            day = callback_query.data[last_sep:]
            date = datetime.datetime(int(saved_date[0]), int(saved_date[1]), int(day), 0, 0, 0)
            cmessageUp(4)
            setDateExpCard(str(date)[0:10])
            for i in range(3):
                if i == 1:
                    await bot.answer_callback_query(callback_query.id)
                if i == 2:
                    messs = await bot.send_message(callback_query.from_user.id, "Создаем карту на дату: " + str(date)[0:10] + "\nВведите описание траты.")
                    setBotLatestMessageId(messs.message_id)
                if i == 0:  
                    await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
        else:
            pass
    
    if 'MONTH' in callback_query.data:
        info = callback_query.data.split(';')
        month_opt = info[0].split('-')[0]
        year, month = int(info[1]), int(info[2])
        chat_id = callback_query.from_user.id
        if month_opt == 'PREV':
            month -= 1
        elif month_opt == 'NEXT':
            month += 1
        if month < 1:
            month = 12
            year -= 1
        if month > 12:
            month = 1
            year += 1
        date = (year, month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month)
        for i in range(3):
            if i == 1:
                await bot.answer_callback_query(callback_query.id)
            if i == 2:
                messs = await bot.send_message(callback_query.from_user.id, "На какой день желаете создать карточку?", reply_markup=markup)
                setBotLatestMessageId(messs.message_id)
            if i == 0:  
                await bot.delete_message(callback_query.from_user.id, getBotLatestMessageId())
    
    if "IGNORE" in callback_query.data:
        await bot.answer_callback_query(callback_query.id, "Это поле пустое. 🙏 не используйте его")
   
    else:
        await bot.answer_callback_query(callback_query.id, text='😐 что-то пошло не по плану...')

@dp.message_handler()
async def echo_message(msg: types.Message):
    if cmessage == 0:
        emailvar = msg.text
        try:
            valid = validate_email(emailvar)
            emailValid = valid.email
            setEmail(emailValid)
            cmessageUp(1)
            for i in range(3):
                if i == 1:
                    await bot.delete_message(msg.chat.id, msg.message_id)
                if i == 2:
                    messs = await bot.send_message(msg.from_user.id, 'Email: ' + emailValid + ' прошел валидацию.\nВведите пароль:')
                    setBotLatestMessageId(messs.message_id)
                if i == 0: 
                    await bot.delete_message(msg.chat.id, getBotLatestMessageId())
        except EmailNotValidError as e:
            print("Ошибка валидации email:  " + str(e))
        except EmailSyntaxError as e:
            print("Ошибка валидации email:  " + str(e))
        except EmailUndeliverableError as e:
            print("Ошибка валидации email:  " + str(e))
        except ValueError as e:
            print("Ошибка валидации email:  " + str(e))
        finally:
            # если имейл не валидный
            for i in range(3):
                if i == 1:
                    await bot.delete_message(msg.chat.id, msg.message_id)
                if i == 2:
                    mess = await bot.send_message(msg.from_user.id, str(e))
                    setBotLatestMessageId(mess.message_id)
                if i == 0: 
                    await bot.delete_message(msg.chat.id, getBotLatestMessageId())
    elif cmessage == 1:
        emailVar = getEmail()
        dataLogin = auth(emailVar, msg.text)
        if dataLogin['totalSize'] == 1:
            if dataLogin['records'][0]['Admin__c'] == True:
                cmessageUp(0)
                print('\n        Успешный вход администратора: ' + dataLogin['records'][0]['LastName'] + '\n        Email: ' + dataLogin['records'][0]['Email'])
                for i in range(3):
                    if i == 1:
                        await bot.delete_message(msg.chat.id, getBotLatestMessageId())
                    if i == 2:
                        mess = await bot.send_message(msg.from_user.id, 'К сожалению для администратора возможностей нет. Воспользуйтесь браузером.', reply_markup=kbStart)
                        setBotLatestMessageId(mess.message_id)
                    if i == 0: 
                        await bot.delete_message(msg.chat.id, msg.message_id)
            else:
                setIdContact(dataLogin['records'][0]['Id'])
                print('\n        Успешный вход пользователя: ' + dataLogin['records'][0]['LastName'] + '\n        Офис: ' + dataLogin['records'][0]['Office__c'] + '\n        Email: ' + dataLogin['records'][0]['Email'])
                cmessageUp(3)
                dateLogin = datetime.datetime.now()
                for i in range(4):
                    if i == 2:
                        await bot.send_message(msg.from_user.id, 'Добро пожаловать ' + dataLogin['records'][0]['LastName'] + '\nВаш офис: ' + dataLogin['records'][0]['Office__c'] + '\nДата и время входа: ' + str(dateLogin)[0:19])
                    elif i == 3:
                        mess = await bot.send_message(msg.from_user.id, 'Ваши дальнейшие действия?', reply_markup=inlineKbAfterLogin)
                        setBotLatestMessageId(mess.message_id)
                    elif i == 1:
                        await bot.delete_message(msg.chat.id, msg.message_id)
                    elif i == 0:
                        await bot.delete_message(msg.chat.id, getBotLatestMessageId())
        elif dataLogin['totalSize'] == 0:
            cmessageUp(0)
            for i in range(3):
                if i == 1:
                    await bot.delete_message(msg.chat.id, getBotLatestMessageId())
                if i == 2:
                    mess = await bot.send_message(msg.from_user.id, 'Ошибка логина или пароля. Повторите попытку входа!\nВведите логин:')
                    setBotLatestMessageId(mess.message_id)
                if i == 0: 
                    await bot.delete_message(msg.chat.id, msg.message_id)
    # elif cmessage == 2:  # действия админа
        # await bot.send_message(msg.from_user.id, 'админ ' + msg.text)
    elif cmessage == 3:  # действия пользователя
        cmessageUp(3)
        for i in range(3):
            if i == 1:
                await bot.delete_message(msg.chat.id, getBotLatestMessageId())
            if i == 2:
                mess = await bot.send_message(msg.from_user.id, 'Извините. Я Вас не понял 😐\nВоспользуйтесь кнопками ниже 👇', reply_markup=inlineKbAfterLogin)
                setBotLatestMessageId(mess.message_id)
            if i == 0: 
                await bot.delete_message(msg.chat.id, msg.message_id)
        
    elif cmessage == 4:  # 2 шаг при добавлении карты
        setDescrExpCard(msg.text)
        cmessageUp(5)
        for i in range(3):
            if i == 1:
                await bot.delete_message(msg.chat.id, msg.message_id)
            if i == 2:
                messs = await bot.send_message(msg.from_user.id, 'Введите сумму (Пример:\n10\n10.1')
                setBotLatestMessageId(messs.message_id)
            if i == 0:  
                await bot.delete_message(msg.chat.id, getBotLatestMessageId())
        
    elif cmessage == 5:  # 3 шаг при добавлении карты
        try:
            msgFloat = float(msg.text)
            setCurrExpCard(str(msg.text))
            cmessageUp(3)
            for i in range(3):
                if i == 1:
                    await bot.delete_message(msg.chat.id, msg.message_id)
                if i == 2:
                    messs = await bot.send_message(msg.from_user.id, 'Данные для новой карточки: ' + '\n' + getCurrExpCard() + '\n' + getDateExpCard() + '\n' + getDescrExpCard(), reply_markup=inlineKbAnsSetCardOrNot)
                    setBotLatestMessageId(messs.message_id)
                if i == 0:  
                    await bot.delete_message(msg.chat.id, getBotLatestMessageId())
        except ValueError:
            cmessageUp(5)
            for i in range(3):
                if i == 1:
                    await bot.delete_message(msg.chat.id, msg.message_id)
                if i == 2:
                    messs = await bot.send_message(msg.from_user.id, 'Введите сумму (Пример:\n10\n10.1')
                    setBotLatestMessageId(messs.message_id)
                if i == 0:  
                    await bot.delete_message(msg.chat.id, getBotLatestMessageId())

        # expectedType = False
        # if isinstance(msg.text, float):
        #     expectedType = True
        # if expectedType == False:
        #     if isinstance(msg.text, int):
        #         expectedType = True
        # if expectedType == False:
        #     cmessageUp(5)
        #     for i in range(3):
        #         if i == 1:
        #             await bot.delete_message(msg.chat.id, msg.message_id)
        #         if i == 2:
        #             messs = await bot.send_message(msg.from_user.id, 'Введите сумму (Пример:\n10\n10.1')
        #             setBotLatestMessageId(messs.message_id)
        #         if i == 0:  
        #             await bot.delete_message(msg.chat.id, getBotLatestMessageId())
        # else:
        #     setCurrExpCard(str(msg.text))
        #     cmessageUp(3)
        #     for i in range(3):
        #         if i == 1:
        #             await bot.delete_message(msg.chat.id, msg.message_id)
        #         if i == 2:
        #             messs = await bot.send_message(msg.from_user.id, 'Данные для новой карточки: ' + '\n' + getCurrExpCard() + '\n' + getDateExpCard() + '\n' + getDescrExpCard(), reply_markup=inlineKbAnsSetCardOrNot)
        #             setBotLatestMessageId(messs.message_id)
        #         if i == 0:  
        #             await bot.delete_message(msg.chat.id, getBotLatestMessageId())



async def on_startup(dp):
    print('Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    print('Bye! Shutting down webhook connection')

def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
