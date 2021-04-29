from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
 
# fdf
# кнопка старта
btnStart = KeyboardButton('/start')
kbStart = ReplyKeyboardMarkup(resize_keyboard=True).row(btnStart)

# кнопки проверки баланса и создания карты
inlineBtnGetBalance = InlineKeyboardButton('Текущий баланс', callback_data='btn_balance')
inlineBtnSetNewExpense = InlineKeyboardButton('Создать карточку', callback_data='btn_setnewcard')
inlineBtnExit = InlineKeyboardButton('Выход', callback_data='btn_exit')
inlineBtnHelp = InlineKeyboardButton('Помощь', callback_data='btn_help')
inlineKbAfterLogin = InlineKeyboardMarkup(row_width=2).row(inlineBtnGetBalance, inlineBtnSetNewExpense).row(inlineBtnExit, inlineBtnHelp)

# кнопки проверки баланса и создания карты
inlineBtnSetDateToday = InlineKeyboardButton('Сегодня', callback_data='btn_setdatetoday')
inlineBtnOpenCalendar = InlineKeyboardButton('Календарь', callback_data='btn_opencalendar')
inlineBtnBackToMain = InlineKeyboardButton('Отмена', callback_data='btn_backtomain')
inlineKbAfterSetNewCard = InlineKeyboardMarkup(row_width=2).row(inlineBtnSetDateToday, inlineBtnOpenCalendar, inlineBtnBackToMain)

# кнопки подтвердить карту или отмена
inlineBtnSetThisExpCard = InlineKeyboardButton('Подтвердить', callback_data='btn_setthisexpcard')
inlineKbAnsSetCardOrNot = InlineKeyboardMarkup(row_width=2).row(inlineBtnSetThisExpCard, inlineBtnBackToMain)