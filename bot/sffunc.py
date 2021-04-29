import logging
import datetime
from simple_salesforce import Salesforce        # подключение библиотеки sf
 

sf = Salesforce(username='expenseappklim@gmail.com', password='vMsaD6gZLTR6RR8', security_token='lTpX3viC0c4EJ3j93YiJCrI5S')

def auth (userLogin, userPass):
    query = "SELECT Id, Email, Password__c, LastName, Admin__c, Office__c FROM Contact WHERE Email = \'" + userLogin + "\' AND Password__c = \'" + userPass + "\' LIMIT 1"
    data = sf.query(query)
    return data
    
def getBalance (userContactId):
    dateNow = datetime.datetime.now()
    yearNow = dateNow.year
    query = "SELECT Id, Month_Date__c, Reminder__c FROM MonthlyExpense__c WHERE Keeper__c = \'" + userContactId + "\' AND CALENDAR_YEAR(Month_Date__c) = " + str(yearNow)
    data = sf.query(query)
    reminder = 0
    for i in data['records']:
        reminder += i['Reminder__c']
    return reminder

def setNewExpCard (userIdContact, dateNewExpCard, currNewExpCard, descrNewExpCard):
    data = sf.ExpenseCard__c.create({'Amount__c' : currNewExpCard, 'CardDate__c' : dateNewExpCard, 'CardKeeper__c' : userIdContact, 'Description__c' : descrNewExpCard})
    logging.info('\nСоздана карта пользователем ' + userIdContact + '\nДанные карты')
    logging.info(data)
    if data['success'] == True:
        return True
    else:
        return False

def getLatestExpCard(idNewExpCard):
    latestExpCard = sf.ExpenseCard__c.get(idNewExpCard)
    logging.info(latestExpCard)
    return latestExpCard