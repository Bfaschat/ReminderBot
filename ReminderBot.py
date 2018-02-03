import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel,
                             QLineEdit, QTextEdit, QMessageBox)
from PyQt5.QtGui import (QPalette, QColor)
from PyQt5.QtCore import (pyqtSlot, pyqtSignal, QTimer)

import sqlite3

import urllib.parse

import ReminderBotHTTP
import ReminderBotSQL
import ReminderBotRE
from datetime import (datetime, timedelta)


# ***************************************************************
# ***************************************************************
# CLASSES

# CURRENT BOT INFORMATION CLASS
class CurrentBot():
    """A class for storing current bot information: token and update number"""
    bot_token = ''
    curr_update_num = 0




# ***************************************************************
# ***************************************************************
# BUTTON CLICK SLOTS


# RUN CYCLE BUTTON PRESSED
@pyqtSlot()
def RunCycleButtonClick():
    """Click on run cycle button for starting main cycle with bot work"""
    PrintInCommandLog('\n')
    if not run_cycle_QTimer.isActive():
        run_cycle_QTimer.start(int(runCyclePeriodLineEdit.text()))

        PrintInCommandLog('->  Cycle timer started successfully.')
    else:
        PrintInCommandLog('->  Error starting cycle timer - it is already started.')


# STOP CYCLE BUTTON PRESSED
@pyqtSlot()
def StopCycleButtonClick():
    """Click on stop cycle button for stopping main cycle with bot work"""
    if run_cycle_QTimer.isActive():
        run_cycle_QTimer.stop()
        db_connection.close()
        PrintInCommandLog('\n->  Cycle timer stopped successfully.')
    else:
        PrintInCommandLog('\n->  Error stopping cycle timer - it is not started.')


# READ TOKEN FROM FILE BUTTON PRESSED
@pyqtSlot()
def ReadTokenFromFileButtonClick():
    bot_info_file = open('bot.info', 'r')
    CurrentBot.bot_token = bot_info_file.readline().strip()
    CurrentBot.curr_update_num = int(bot_info_file.readline().strip())
    currTokenLineEdit.setText(CurrentBot.bot_token)
    currUpdateNumLineEdit.setText(str(CurrentBot.curr_update_num))
    bot_info_file.close()


# CHECK TOKEN BY SENDING SPECIAL REQUEST
@pyqtSlot()
def TestBotTokenButtonClick():
    commandLogTextEdit.append('\n -> Sending "getMe" request with current token.')
    if len(CurrentBot.bot_token) == 0:
        PrintInCommandLog("""    Can't send "getMe" request as current token is empty.""")
    else:
        PrintInCommandLog("    The answer:")
        [result, decoded_answer] = ReminderBotHTTP.GetMeRequest(bot_start_URL, CurrentBot.bot_token)
        if result == 1:     # EXCEPTION OCCURED
            PrintInCommandLog('    An error has occured during "getMe" request: ' + decoded_answer)
        else:               # NO EXCEPTIONS
            commandLogTextEdit.append(str(decoded_answer))
            if decoded_answer['ok'] is True:
                PrintInCommandLog("    The check is complete successful.")


# CLEAR COMMAND LOG BUTTON PRESSED
@pyqtSlot()
def CommandLogClearButtonClick():
    """Click on command log clean button for clearing the command log"""
    commandLogTextEdit.clear()


# EXPORT COMMAND LOG BUTTON PRESSED
@pyqtSlot()
def CommandLogExportButtonClick():
    """Click on command log export button for exporting the command log content to the file with name "CommandLog<CurrentDateAndTime>.log"""
    commandLogFile = open('CommandLog' + str(datetime.now()) + '.log', 'w')
    commandLogFile.write(commandLogTextEdit.plainText)
    commandLogFile.close()


# CLEAR CHAT LOG BUTTON PRESSED
@pyqtSlot()
def ChatLogClearButtonClick():
    """Click on chat log clean button for clearing the chat log"""
    chatLogTextEdit.clear()


# EXPORT CHAT LOG BUTTON PRESSED
@pyqtSlot()
def ChatLogExportButtonClick():
    """Click on chat log export button for exporting the chat log content to the file with name "ChatLog<CurrentDateAndTime>.log"""
    chat_log_file = open('ChatLog' + str(datetime.now()) + '.log', 'w')
    chat_log_file.write(chatLogTextEdit.plainText)
    chat_log_file.close()


# CLEAR DB LOG BUTTON PRESSED
@pyqtSlot()
def DBLogClearButtonClick():
    """Click on DB log clean button for clearing the DB log"""
    DBLogTextEdit.clear()


# EXPORT DB LOG BUTTON PRESSED
@pyqtSlot()
def DBLogExportButtonClick():
    """Click on chat log export button for exporting the command log content to the file with name "ChatLog<CurrentDateAndTime>.log"""
    DB_log_file = open('DBLog' + str(datetime.now()) + '.log', 'w')
    DB_log_file.write(DBLogTextEdit.plainText)
    DB_log_file.close()


# SHOW ALL SOURCES BUTTON PRESSED
@pyqtSlot()
def ShowAllSourceButtonClick():
    """Getting all registered in BD sources and printing them to command log"""
    sources = ReminderBotSQL.GetAllSources(db_filename)
    if sources == -1:
        PrintInCommandLog('\n->  Error getting all sources from DB.')
        return 1
    else:
        PrintInCommandLog('\n->  Printing all currently saved sources.')
        PrintInDBLog('\n->  All currently saved sources:')
        for source in sources:
            tmp_str = ''
            for field in source:
                tmp_str += str(field) + ' '
            PrintInDBLog('- ' + tmp_str)
        return 0


# SHOW ALL NOTES BUTTON PRESSED
@pyqtSlot()
def ShowAllNotesButtonClick():
    """Getting all registered in BD notes and printing them to command log"""
    notes = ReminderBotSQL.GetAllNotes(db_filename)
    if notes == -1:
        PrintInCommandLog('\n->  Error getting all notes from DB.')
        return 1
    else:
        PrintInCommandLog('\n->  Printing all currently saved notes.')
        PrintInDBLog('\n->  All currently saved notes:')
        for note in notes:
            tmp_str = ''
            for field in note:
                tmp_str += str(field) + ' '
            PrintInDBLog('--> ' + tmp_str)
        return 0


# CLEAR SOURCES TABLE BUTTON PRESSED
@pyqtSlot()
def ClearSourcesTableButtonClick():
    """Clearing table, containing sources data"""
    if ReminderBotSQL.ClearSourcesTable(db_filename) != 0:
        PrintInCommandLog('\n->  Error while erasing Sources table.')
    else:
        PrintInCommandLog('\n->  Sources table erased successfully.')


# CLEAR NOTES TABLE BUTTON PRESSED
@pyqtSlot()
def ClearNotesTableButtonClick():
    """Clearing table, containing notes data"""
    if ReminderBotSQL.ClearNotesTable(db_filename) != 0:
        PrintInCommandLog('\n->  Error while erasing Notes table.')
    else:
        PrintInCommandLog('\n->  Notes table erased successfully.')


# TEXT BUTTON PRESSED
@pyqtSlot()
def TestButtonClick():
    """Button for some tests"""
    result = urllib.parse.quote(currTokenLineEdit.text())
    print(str(result))



# ***************************************************************
# ***************************************************************
# EVENTS

# MAIN WINDOW QWIDGET IS CLOSING
@pyqtSlot()
def MainWindowCloseEvent():
    """Event of program going to quit - for finalization"""
    bot_info_file = open('bot.info', 'r')
    CurrentBot.bot_token = bot_info_file.readline().strip()
    bot_info_file.close()
    bot_info_file = open('bot.info', 'w')
    bot_info_file.write(CurrentBot.bot_token + '\n')
    bot_info_file.write(str(CurrentBot.curr_update_num))
    bot_info_file.close()
    #ReminderBotSQL.CloseConnectionToDB(db_connection)
    #db_connection.close()
    if run_cycle_QTimer.isActive():
        run_cycle_QTimer.stop()

    print('We are closing...')


# THE RUN CYCLE TIMER ACTION
@pyqtSlot()
def RunCycleTimerAction():
    """The action of main run cycle timer with bot work"""
    # CHECK LOGS
    if len(commandLogTextEdit.toPlainText()) > 100000:
        commandLogFile = open('CommandLog' + str(datetime.now()) + '.log', 'w')
        commandLogFile.write(commandLogTextEdit.plainText)
        commandLogFile.close()
        commandLogTextEdit.clear()

    if len(chatLogTextEdit.toPlainText()) > 100000:
        chat_log_file = open('ChatLog' + str(datetime.now()) + '.log', 'w')
        chat_log_file.write(commandLogTextEdit.plainText)
        chat_log_file.close()
        chatLogTextEdit.clear()

    # REQUESTING UPDATES
    if len(CurrentBot.bot_token) == 0:
        PrintInCommandLog("""\n->  Can't send "getUpdate" request as current token is empty.""")
        #force_stop_cycle.emit()
        StopCycleButtonClick()
        return 1

    PrintInCommandLog('\n->  Sending "getUpdates" request with token:\n' + CurrentBot.bot_token +
                      '\n   and update number:\n' + str(CurrentBot.curr_update_num + 1))
    [result, decoded_answer] = ReminderBotHTTP.SendGetUpdatesRequest(CurrentBot.curr_update_num + 1, 100, 2, CurrentBot.bot_token)
    if result == 1:         # IF AN EXCEPTION OCCURED
        PrintInCommandLog('    An error has occured during "getUpdates" request: ' + decoded_answer)
        #force_stop_cycle.emit()
        StopCycleButtonClick()
        return 1

    # IF NO EXCEPTIONS
    db_connection = ReminderBotSQL.ConnectToDB(db_filename, None)

    # CHECKING THE ANSWER
    if len(decoded_answer['result']) == 0:
        PrintInCommandLog('\n->  No updates received.')
    else:
        CurrentBot.curr_update_num = decoded_answer['result'][-1]['update_id']
        currUpdateNumLineEdit.setText(str(CurrentBot.curr_update_num))

        PrintInCommandLog(str(decoded_answer))

        # PROCESSING UPDATES
        for update in decoded_answer['result']:
            # PRINTING MESSAGES TO CHAT LOG
            PrintInChatLog('\n->  Message from: ' + update['message']['from']['first_name'] + ' ' +
                           update['message']['from']['first_name'] + '\n' + update['message']['text'])

            source_id = update['message']['chat']['id']
            message = str(update['message']['text']).strip()
            # GETTING CURRENT SOURCE STATE
            source_state = ReminderBotSQL.CheckSourceState(source_id, db_connection)
            is_user = True
            user_language = 'eng'
            if source_state == -1:
                PrintInCommandLog('->  Error checking source state: error executing through DB connection.')
                StopCycleButtonClick()
                return 1
            if source_state == -3:
                PrintInCommandLog('->  Error checking source state: more than one example of the source in DB.')
                StopCycleButtonClick()
                return 1
            if source_state == -2:
                # ADDING SOURCE TO BD IF IT IS NEW
                if ReminderBotSQL.AddSource(source_id, db_connection, is_user, user_language) == 1:
                    PrintInCommandLog('->  Error adding a source to the DB.')
                    StopCycleButtonClick()
                    return 1

                PrintInCommandLog('\n->  A source is added to DB: ' + str(source_id) + ', is a user: ' + str(is_user) +
                                  ', language: ' + user_language)

            # LOGIC OF STATE AND MESSAGE

            # PROCESSING HELP COMMAND
            if message.lower() in ('/help', 'help'):
                answer_to_source = ('Hi, I am the <b>reminder bot</b>! And I am at your service.\n'
                                      'You can send me next commands:\n'
                                      '/help - for getting this help message,\n'
                                      '/show - to see all your notes I still remember,\n'
                                      '/save - to save a note that I will remind you on time,\n'
                                      '/delay - to delay last note reminded by me not longer ago then 30 min.\n'
                                      'You can type that commands manually without "/" symbol.')
                if SendMessageToChatLogged(source_id, answer_to_source, 'HTML',
                                        bot_start_URL, CurrentBot.bot_token) != 0:
                    return 1

                # CHANGING SOURCE STATE TO 0 - DEFAULT
                if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                    return 1

                continue

            # PROCESSING SHOW COMMAND
            if message.lower() in ('/show', 'show'):
                # GETTING NOTES OF CURRENT SOURCE
                notes = ReminderBotSQL.GetAllNotesOfSource(source_id, db_connection)
                if notes == -1:
                    PrintInCommandLog('->  Error getting notes from DB.')
                    StopCycleButtonClick()
                    return 1

                if notes is None or len(notes) == 0:
                    answer_to_source = 'You have no saved not-reminded notes to show. Use /help to get help with list of all commands.'
                else:
                    # ADDING FOUND NOTES TO THE ANSWER
                    answer_to_source = "Your saved notes are:"
                    for note in notes:
                        answer_to_source += ('\n' + str(note[0]) + '.' + str(note[1]) + '.' + str(note[2]) + ' '
                                             + str(note[3]) + ':' + str(note[4]) + '\n"' + note[5]) + '"'
                        if note[6] == 1:
                            answer_to_source += ' (reminded)'

                    answer_to_source += "\nUse /help for help."

                if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                    return 1

                # CHANGING SOURCE STATE TO 0 - DEFAULT
                if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                    return 1

                continue

            # PROCESSING SAVE COMMAND
            if message.lower() in ('/save', 'save'):
                answer_to_source = ('Enter the note to remind in format: YYYY.MM.DD hh:mm text\n'
                'or hh:mm text\n'
                'where YYYY.MM.DD hh:mm - date and time to remind the text (without date - today time):\n'
                'YYYY - 4 digits of the year\n'
                'MM - 2 digits of the month\n'
                'DD - 2 digits of the day\n'
                'hh - 2 digits of the hour\n'
                'mm - 2 digits of the minutes.\n'
                'text length must be at least 3 characters\n'
                'Example: "2012.08.16 15:20 Call mom"')
                if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                    return 1

                # CHANGING SOURCE STATE TO 1 - WAITING FOR MESSAGE IN FORMAT TO REMIND
                if ChangeSourceStateLogged(source_id, db_connection, 1) != 0:
                    return 1

                continue

            # PROCESSING DELAY COMMAND
            if message.lower() in ('/delay', 'delay'):
                # GETTING LAST REMINDED NOTE IN PAST 30 MINUTES OF CURRENT SOURCE
                note = GetLastRemindedNoteLogged(source_id, db_connection)
                if note == -1:
                    return 1

                if note == 0:
                    answer_to_source = ('You have no recently reminded note to delay (no notes where reminded last 30 minutes). '
                                       'Use /save command first to save a note or /help for help.')
                    if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                        return 1

                    # CHANGING SOURCE STATE TO 0 - DEFAULT
                    if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                        return 1

                    continue

                else:
                    answer_to_source = ('Enter the delay period in format:\n' 
                                        'YYYY.MM.DD hh:mm (time to remind again) or hh:mm (timegap to delay from current moment)\n'
                                        'for the message:\n' + str(note[6]) +
                                        '\nwhere:\n'
                                        'YYYY - 4 digits of the year\n'
                                        'MM - 2 digits of the month\n'
                                        'DD - 2 digits of the day\n'
                                        'hh - 2 digits of the hour\n'
                                        'mm - 2 digits of the minutes.\n'
                                        'Example: "2012.08.18 15:40" or "02:30"')
                    if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                        return 1

                    # CHANGING SOURCE STATE TO 2 - WAITING FOR MESSAGE IN FORMAT TO DELAY
                    if ChangeSourceStateLogged(source_id, db_connection, 2) != 0:
                        return 1

                    continue

            # PROCESSING TIME COMMAND
            if message.lower() in ('/time', 'time'):
                answer_to_source = 'Server time is: ' + str(datetime.now())
                if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                    return 1

                # CHANGING SOURCE STATE TO 0 - DEFAULT
                if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                    return 1

                continue

            # PROCESSING MESSAGE WITHOUT A COMMAND

            # AFTER SAVE COMMAND
            if source_state == 1:
                # CHECKING THE UPDATE MESSAGE TO HAVE THE FORMAT "DATE TIME TEXT"
                check_result = ReminderBotRE.CheckForDateTimeText(message)
                if check_result == 0:
                    # THE UPDATE MESSAGE WAS INCORRECT
                    answer_to_source = ('The entered note does not match the format: YYYY.MM.DD hh:mm text\nPlease,'
                                       'try again. You can use /save to see the description of format or /help for help.')

                else:
                    answer_to_source = """Your note has been saved. I will kindly remind it to you on time. Use /help for help."""

                # GATTING DATETIME FOR DATE TIME TEXT FORMAT
                if check_result == 1:
                    year = int(message[0:4])
                    month = int(message[5:7])
                    day = int(message[8:10])
                    message = message[10:].lstrip()
                    hour = int(message[0:2])
                    minute = int(message[3:5])
                    text = message[5:].lstrip()

                # GETTING DATETIME FOR TIME TEXT FORMAT
                if check_result == 2:
                    current_day = datetime.now()
                    year = current_day.year
                    month = current_day.month
                    day = current_day.day
                    hour = int(message[0:2])
                    minute = int(message[3:5])
                    text = message[5:].lstrip()

                if check_result > 0:
                    if len(text) < 3:
                        answer_to_source = ('Your note text is too short (less then 3 symbols). Please,'
                                    'try again. You can use /save to see the description of format or /help for help.')

                    else:
                        # THE UPDATE MESSAGE IS CORRECT - SAVING NOTE TO DB
                        if ReminderBotSQL.AddNote(source_id, db_connection, year, month, day, hour, minute, text) != 0:
                            PrintInCommandLog("->  Error adding a note through DB connection.")
                            StopCycleButtonClick()
                            return 1

                        # CHANGING SOURCE STATE TO 0 - DEFAULT
                        if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                            return 1

                if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                    return 1

                continue

            # AFTER DELAY COMMAND
            if source_state == 2:
                # CHECKING THE UPDATE MESSAGE TO HAVE THE FORMAT "DATE TIME" OR "TIME"
                check_result = ReminderBotRE.CheckForDateTimeOrTime(message)
                if check_result == 0:
                    # THE UPDATE MESSAGE WAS INCORRECT
                    answer_to_source = ('The entered delay does not match the format:\n'
                                        'YYYY.MM.DD hh:mm or hh:mm\n'
                                        'Please, try again. You can use /delay to see the description of format or /help for help.')
                else:
                    # MESSAGE CORRECT - GETTING LAST REMINDED NOTE NOT OLDER THEN 30 MINUTES
                    note = GetLastRemindedNoteLogged(source_id, db_connection)
                    if note == -1:
                        return 1

                    if note == 0:
                        answer_to_source = ('Your last note is no longer available to delay. You can delay a note not' 
                                            'longer then next 30 minutes after it has been reminded. Use /help for help.')
                    else:
                        answer_to_source = 'Your message\n"' + note[6] + '"\nhas been delayed. Use /help for help.'

                # ACQUIRING NEW TIME FOR THE NOTE TO REMIND
                if check_result == 1:
                    # THE UPDATE MESSAGE IS CORRECT AND HOLD NEW DATE TIME
                    year = int(message[0:4])
                    month = int(message[5:7])
                    day = int(message[8:10])
                    message = message[10:].lstrip()
                    hour = int(message[0:2])
                    minute = int(message[3:5])

                if check_result == 2:
                    # THE UPDATE MESSAGE IS CORRECT AND HOLD DELAY TIME
                    hour = int(message[0:2])
                    minute = int(message[3:5])
                    new_datetime = datetime.now() + timedelta(0, 0, 0, 0, minute, hour)
                    year = new_datetime.year
                    month = new_datetime.month
                    day = new_datetime.day
                    hour = new_datetime.hour
                    minute = new_datetime.minute

                if check_result > 0 and note != 0 and note != -1:
                    # UPDATING NOTE DATA AND REMINDED STATUS
                    if ReminderBotSQL.DelayNote(note[0], db_connection, year, month, day, hour, minute) != 0:
                        PrintInCommandLog('\n->  Error delaying note ID: ' + str(note[0]) + ' .')
                        StopCycleButtonClick()

                    # CHANGING SOURCE STATE TO 0 - DEFAULT
                    if ChangeSourceStateLogged(source_id, db_connection, 0) != 0:
                        return 1

                if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                    return 1

                continue

            # IF MESSAGE CONTAINS NO COMMAND AND NO CERTAIN DATA REQUIRED FROM SOURCE (STATE = 0)
            answer_to_source = ('Hi, I am the <b>reminder bot</b>! And I am at your service.%0A'
                               'You can send me next commands:\n'
                               '/help - for getting this help message,\n'
                               '/show - to see all your notes I still remember,\n'
                               '/save - to save a note that I will remind you on time,\n'
                               '/delay - to delay last note reminded by me not longer ago then 30 min.\n'
                               'You can type that commands manually without "/" symbol.')
            if SendMessageToChatLogged(source_id, answer_to_source) != 0:
                return 1

            # END OF FOR LOOP OF UPDATES

    # REMINDING ALL NOTES WITH PASSED DATETIME AND REMINDED = 0
    notes = ReminderBotSQL.GetNotesToRemind(db_connection)
    if notes == -1:
        PrintInCommandLog('->  Error getting notes to remind from DB.')
        StopCycleButtonClick()
        return 1

    if notes != -2:
        sent_notes_id = ''
        for note in notes:
            source_id = note[1]
            remind_datetime = datetime(note[2], note[3], note[4], note[5], note[6])
            if (datetime.now() - remind_datetime).total_seconds() > 0:
                message_to_source = 'Kindly reminding:\n' + str(remind_datetime) + '\n' + note[7]
                if SendMessageToChatLogged(source_id, message_to_source) != 0:
                    return 1

                sent_notes_id+= str(note[0]) + ', '

        # CHANGING PREVIOUSLY PROCESSED NOTES REMINDED TO 1
        if len(sent_notes_id) > 0:
            sent_notes_id = sent_notes_id[0:-2]
            if ReminderBotSQL.ChangeNotesToReminded(db_connection, sent_notes_id) != 0:
                PrintInCommandLog('->  Error changing notes to reminded in DB.')
                StopCycleButtonClick()
                return 1

    # REMOVING ALL OLD NOTES
    if ReminderBotSQL.RemoveOldRemindedNotes(db_connection) != 0:
        PrintInCommandLog('->  Error removing old reminded notes from DB.')
        StopCycleButtonClick()
        return 1

    db_connection.close()


# CHANGE OF TOKEN LINEEDIT
@pyqtSlot()
def CurrTokenLineEditChange():
    """When current bot token is changed manually in lineedit - copying it to the holding class"""
    CurrentBot.bot_token = currTokenLineEdit.text()


# ***************************************************************
# ***************************************************************
# CHECKS

# THE CURRENT UPDATE NUMBER IS EDITED (NOT CHANGED) IN FORM
@pyqtSlot()
def CurrUpdateNumLineEditChange():
    """Event of current update lineedit edited (not changed), that copies the new value to the holding class"""
    CurrentBot.curr_update_num = int(currUpdateNumLineEdit.text())


@pyqtSlot()
def RunCyclePeriodLineEditChange():
    """Event of run cycle period lineedit change, checking new value to be an int number"""
    if len(runCyclePeriodLineEdit.text()) == 0 or not runCyclePeriodLineEdit.text().isdigit():
        runCyclePeriodLineEdit.setText('300')


# ***************************************************************
# ***************************************************************
# OTHER FUNCTIONS

def PrintInCommandLog(text):
    """Printig TEXT in the command log """
    commandLogTextEdit.append(text)


def PrintInChatLog(text):
    """Printig TEXT in the chat log """
    chatLogTextEdit.append(text)


def PrintInDBLog(text):
    """Printig TEXT in the DB log """
    DBLogTextEdit.append(text)


def SendMessageToChatLogged(chat_id, text, parse_mode='HTML', startURL=None, token=None):
    """Sending message to chat with logging of process"""
    if startURL is None:
        startURL = bot_start_URL

    if token is None:
        token = CurrentBot.bot_token

    [result, decoded_answer] = ReminderBotHTTP.SendMessageToChat(chat_id, text, parse_mode, startURL, token)
    if result == 1:
        PrintInCommandLog('    An error has occured during "sendMessage" request: ' + decoded_answer)
        StopCycleButtonClick()
        return 1

    PrintInChatLog('->  Message to: ' + str(chat_id) + '\n' + text)
    return 0


def ChangeSourceStateLogged(source_id, db_connection, new_state):
    """Changing the source <source_id> state to <new_state> through <db_connection>"""
    if ReminderBotSQL.ChangeSourceState(source_id, db_connection, new_state) != 0:
        PrintInCommandLog("->  Error changing source " + str(source_id) + " state to " + str(new_state) + " through DB connection.")
        StopCycleButtonClick()
        return 1

    return 0


def GetLastRemindedNoteLogged(update_source_id, db_connection):
    """Getting last note of the source that was reminded in last 30 minutes"""
    note = ReminderBotSQL.GetLastRemindedNoteOfSource(update_source_id, db_connection)
    if note == -1:
        PrintInCommandLog('->  Error getting last reminded note from DB.')
        StopCycleButtonClick()
        return -1

    if note == -2:
        return 0

    return note


# ***************************************************************
# ***************************************************************
# MAIN PROGRAM RUN

if __name__ == '__main__':
    # VARIABLES

    bot_start_URL = r'https://api.telegram.org/bot'
    db_filename = 'SourcesAndNotes.db'
    run_cycle_QTimer = QTimer()
    run_cycle_QTimer.timeout.connect(RunCycleTimerAction)
    db_connection = sqlite3.connect(":memory:")

    # INTERFACE INITIALIZATION

    app = QApplication(sys.argv)

    mainVBox = QVBoxLayout()
    topExitButtonHBox = QHBoxLayout()
    topButtonTokenGrid = QGridLayout()
    middleLogGrid = QGridLayout()
    bottomDBGrid = QGridLayout()
    bottomCycleHBox = QHBoxLayout()

    # PALLETS

    buttonPalette = QPalette()
    lineEditPalette = QPalette()

    buttonPalette.setColor(buttonPalette.Button, QColor(50, 100, 255))
    lineEditPalette.setColor(lineEditPalette.Base, QColor(220, 220, 220))

    # WIDGETS AND LAYOUTS

    exitButton = QPushButton("Exit")
    exitButton.setPalette(buttonPalette)
    exitButton.clicked.connect(QApplication.instance().quit)

    QApplication.instance().lastWindowClosed.connect(MainWindowCloseEvent)
    QApplication.instance().aboutToQuit.connect(MainWindowCloseEvent)

    topExitButtonHBox.addStretch(1)
    topExitButtonHBox.addWidget(exitButton)

    readTokenFromFileButton = QPushButton("Read bot token from file")
    readTokenFromFileButton.setPalette(buttonPalette)
    readTokenFromFileButton.clicked.connect(ReadTokenFromFileButtonClick)

    testBotTokenButton = QPushButton("Test the token")
    testBotTokenButton.setPalette(buttonPalette)
    testBotTokenButton.clicked.connect(TestBotTokenButtonClick)

    tokenLabel = QLabel("Current token:")

    updateNumLabel = QLabel("Last update number (enter -102 for getting all updates):")

    currTokenLineEdit = QLineEdit()
    currTokenLineEdit.setPalette(lineEditPalette)
    currTokenLineEdit.textChanged.connect(CurrTokenLineEditChange)

    currUpdateNumLineEdit = QLineEdit()
    #currUpdateNumLineEdit.setReadOnly(True)
    currUpdateNumLineEdit.setPalette(lineEditPalette)
    currUpdateNumLineEdit.editingFinished.connect(CurrUpdateNumLineEditChange)

    topButtonTokenGrid.addWidget(readTokenFromFileButton, 0, 0)
    topButtonTokenGrid.addWidget(testBotTokenButton, 1, 0)
    topButtonTokenGrid.addWidget(tokenLabel, 0, 2)
    topButtonTokenGrid.addWidget(updateNumLabel, 1, 2)
    topButtonTokenGrid.addWidget(currTokenLineEdit, 0, 3)
    topButtonTokenGrid.addWidget(currUpdateNumLineEdit, 1, 3)

    commandLogLabel = QLabel("Command log:")

    chatLogLabel = QLabel("Chat log:")

    commandLogTextEdit = QTextEdit()
    commandLogTextEdit.setFixedHeight(400)
    commandLogTextEdit.setFixedWidth(600)
    commandLogTextEdit.setPalette(lineEditPalette)

    chatLogTextEdit = QTextEdit()
    chatLogTextEdit.setPalette(lineEditPalette)
    chatLogTextEdit.setFixedWidth(600)

    commandLogClearButton = QPushButton("Clear command log")
    commandLogClearButton.setPalette(buttonPalette)
    commandLogClearButton.clicked.connect(CommandLogClearButtonClick)

    commandLogExportButton = QPushButton("Export command log")
    commandLogExportButton.setPalette(buttonPalette)
    commandLogExportButton.clicked.connect(CommandLogExportButtonClick)

    chatLogClearButton = QPushButton("Clear chat log")
    chatLogClearButton.setPalette(buttonPalette)

    chatLogExportButton = QPushButton("Export chat log")
    chatLogExportButton.setPalette(buttonPalette)

    middleLogGrid.addWidget(commandLogLabel, 0, 0)
    middleLogGrid.addWidget(chatLogLabel, 0, 3)
    middleLogGrid.addWidget(commandLogTextEdit, 1, 0, 1, 2)
    middleLogGrid.addWidget(chatLogTextEdit, 1, 3, 1, 2)
    middleLogGrid.addWidget(commandLogClearButton, 2, 0)
    middleLogGrid.addWidget(commandLogExportButton, 2, 1)
    middleLogGrid.addWidget(chatLogClearButton, 2, 3)
    middleLogGrid.addWidget(chatLogExportButton, 2, 4)

    DBLogLabel = QLabel("DB log:")

    showAllSourcesButton = QPushButton("Show all registered sources")
    showAllSourcesButton.setPalette(buttonPalette)
    showAllSourcesButton.clicked.connect(ShowAllSourceButtonClick)

    showAllNotesButton = QPushButton("Show all registered notes")
    showAllNotesButton.setPalette(buttonPalette)
    showAllNotesButton.clicked.connect(ShowAllNotesButtonClick)

    showSourcesStatisticsButton = QPushButton("Show sources statistics")
    showSourcesStatisticsButton.setPalette(buttonPalette)
    #showSourcesStatisticsButton.clicked.connect(ShowSourcesStatisticsButtonClick)

    showNotesStatisticsButton = QPushButton("Show notes statistics")
    showNotesStatisticsButton.setPalette(buttonPalette)
    #showNotesStatisticsButton.clicked.connect(ShowNotesStatisticsButtonClick)

    clearSourcesTableButton = QPushButton("Clear sources table")
    clearSourcesTableButton.setPalette(buttonPalette)
    clearSourcesTableButton.clicked.connect(ClearSourcesTableButtonClick)

    clearNotesTableButton = QPushButton("Clear notes table")
    clearNotesTableButton.setPalette(buttonPalette)
    clearNotesTableButton.clicked.connect(ClearNotesTableButtonClick)

    DBLogClearButton = QPushButton("Clear DB log")
    DBLogClearButton.setPalette(buttonPalette)
    DBLogClearButton.clicked.connect(DBLogClearButtonClick)

    DBLogExportButton = QPushButton("Export DB log")
    DBLogExportButton.setPalette(buttonPalette)
    DBLogExportButton.clicked.connect(DBLogExportButtonClick)

    DBLogTextEdit = QTextEdit()
    DBLogTextEdit.setFixedHeight(200)
    DBLogTextEdit.setFixedWidth(600)
    DBLogTextEdit.setPalette(lineEditPalette)

    bottomDBGrid.addWidget(DBLogLabel, 0, 2)
    bottomDBGrid.addWidget(showAllSourcesButton, 1, 0)
    bottomDBGrid.addWidget(showAllNotesButton, 1, 1)
    bottomDBGrid.addWidget(DBLogTextEdit, 1, 2, 4, 1)
    bottomDBGrid.addWidget(showSourcesStatisticsButton, 2, 0)
    bottomDBGrid.addWidget(showNotesStatisticsButton, 2, 1)
    bottomDBGrid.addWidget(clearSourcesTableButton, 3, 0)
    bottomDBGrid.addWidget(clearNotesTableButton, 3, 1)
    bottomDBGrid.addWidget(DBLogClearButton, 4, 0)
    bottomDBGrid.addWidget(DBLogExportButton, 4, 1)


    runCycleButton = QPushButton("Run bot cycle")
    runCycleButton.setPalette(buttonPalette)
    runCycleButton.clicked.connect(RunCycleButtonClick)

    stopCycleButton = QPushButton("Stop bot cycle")
    stopCycleButton.setPalette(buttonPalette)
    stopCycleButton.clicked.connect(StopCycleButtonClick)

    runCycleOnceButton = QPushButton("Run bot cycle ONCE")
    runCycleOnceButton.setPalette(buttonPalette)
    runCycleOnceButton.clicked.connect(RunCycleTimerAction)

    testButton = QPushButton("Tst")
    testButton.setPalette(buttonPalette)
    testButton.clicked.connect(TestButtonClick)

    runCyclePeriodLabel = QLabel("Cycle period, ms:")

    runCyclePeriodLineEdit = QLineEdit()
    runCyclePeriodLineEdit.setPalette(lineEditPalette)
    runCyclePeriodLineEdit.setText('5000')
    runCyclePeriodLineEdit.textChanged.connect(RunCyclePeriodLineEditChange)

    bottomCycleHBox.addWidget(runCycleButton)
    bottomCycleHBox.addWidget(stopCycleButton)
    bottomCycleHBox.addWidget(runCycleOnceButton)
    bottomCycleHBox.addStretch(1)
    bottomCycleHBox.addWidget(testButton)
    bottomCycleHBox.addStretch(1)
    bottomCycleHBox.addWidget(runCyclePeriodLabel)
    bottomCycleHBox.addWidget(runCyclePeriodLineEdit)

    mainVBox.addLayout(topExitButtonHBox)
    mainVBox.addLayout(topButtonTokenGrid)
    mainVBox.addLayout(middleLogGrid)
    mainVBox.addLayout(bottomDBGrid)
    mainVBox.addLayout(bottomCycleHBox)
    mainVBox.addStretch(1)

    mainWindow = QWidget()
    mainWindow.setLayout(mainVBox)
    mainWindow.setGeometry(300, 50, 1200, 800)

    mainWindow.setWindowTitle('Reminder Bot V 1.0')
    mainWindow.show()

    sys.exit(app.exec_())