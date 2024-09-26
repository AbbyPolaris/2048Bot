import os
import telebot
import random

from aiogram.types import KeyboardButton , ReplyKeyboardMarkup , ReplyKeyboardRemove


class bot():
    def __init__(self) -> None:
        self.buttons = "{\"keyboard\":[[{\"text\":\"Up\"}],[{\"text\":\"Left\"},{\"text\":\"Down\"},{\"text\":\"Right\"}]]}"
        self.API_KEY = "Your telegram bot API"
        self.direction = {'L': 0, 'D': 1, 'R': 2, 'U': 3, 'X': 4}
        self.bot = telebot.TeleBot(self.API_KEY)
        self.loseOfAccs = {}
        self.scoreOfAccs = {}
        self.gridMessageOfAccs = {}
        self.scoremessageOfAccs = {}
        self.gridOfAccs = {}
        pass
    def rotate(self,grid):
        return list(map(list, zip(*grid[::-1])))
    def move(self,grid, dir , message):
        for i in range(dir): grid = self.rotate(grid)
        for i in range(len(grid)):
            temp = []
            for j in grid[i]:
                if j != '.':
                    temp.append(j)
            temp += ['.'] * grid[i].count('.') 
            for j in range(len(temp) - 1):
                if temp[j] == temp[j + 1] and temp[j] != '.' and temp[j + 1] != '.':
                    temp[j] = str(2 * int(temp[j]))
                    self.scoreOfAccs[message.chat.id] += int(temp[j])
                    temp[j + 1] = '.'
            grid[i] = []
            for j in temp:
                if j != '.':
                    grid[i].append(j)
            grid[i] += ['.'] * temp.count('.')
        for i in range(4 - dir): grid = self.rotate(grid)
        return grid

    def printGrid(self,grid , chatid , flag , loseStatus):
        strResult = "\n"
        strResult += '+-------+-------+-------+-------+\n'
        for i in range(len(grid)):
            res = ""
            res+='|       |       |       |       |\n'
            res+='|'
            for j in range(len(grid[i])):
                
                spaceres = ""
                isdotcoord = 2
                if(grid[i][j] == "."):
                    isdotcoord = 0
                Oddlen = 1
                if(len(str(grid[i][j]))%2 == 0):
                    Oddlen = 0
                for _ in range(int((7 - len(str(grid[i][j])))/2)-Oddlen): spaceres += " "
                res+= spaceres
                if(grid[i][j] == "."):
                    res += " "
                else:
                    res +=   grid[i][j]            
                for _ in range(int((7 - len(str(grid[i][j])))/2)+1): res += " "
                res += "|"
            res+='\n'
            res+='|       |       |       |       |\n'
            res += '+-------+-------+-------+-------+\n'
            strResult += (res)
            
        if not flag:
            gridmessage = bot.send_message(chatid , '```'+strResult+'```' , parse_mode= 'Markdown')
            self.gridMessageOfAccs.update({chatid : gridmessage})
            print(strResult)
        else:
            try:
                bot.edit_message_text(chat_id=chatid, message_id=self.gridMessageOfAccs[chatid].message_id, text='```'+strResult+'```',parse_mode= 'Markdown')
            except:
                print(loseStatus)
                if loseStatus:
                    try:
                        bot.edit_message_text(chat_id=chatid, message_id=self.gridMessageOfAccs[chatid].message_id, text="game is ended , use /game")
                    except:
                        print("exception2")
    def findEmptySlot(self,grid):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == '.':
                    return (i, j, 0)
        return (-1, -1, 1)


    def addNumber(self,grid):
        num = random.randint(1, 2) * 2
        x = random.randint(0, 3)
        y = random.randint(0, 3)
        lost = 0
        if grid[x][y] != '.':
            x, y, lost = self.findEmptySlot(grid)
        if not lost: grid[x][y] = str(num)
        return (grid, lost)

        
    def startGame(self,message):
        print(self.scoremessageOfAccs)
        chatid = message.chat.id
        bot.send_message(message.chat.id , "Combine given numbers to get a maximum score.\nYou can move numbers to left, right, up or down direction. use /X to exit\n" , reply_markup = self.buttons)
        scoremessage = bot.send_message(message.chat.id , "score: 0")
        self.scoremessageOfAccs.update({message.chat.id : scoremessage})

        grid = [['.', '.', '.', '.'],
                ['.', '.', '.', '.'],
                ['.', '.', '.', '.'],
                ['.', '.', '.', '.']]
        random_pick_array = ['.','.','.','2','4']
        for i in range(4):
            for j in range(4):
                grid[i][j] = random_num = random.choice(random_pick_array)

        self.gridOfAccs.update({message.chat.id : grid})        
        self.printGrid(self.gridOfAccs[message.chat.id] , chatid  , False , 0)
        
        loseStatus = 0
        score = 0
        self.loseOfAccs.update({message.chat.id : loseStatus})
        self.scoreOfAccs.update({message.chat.id : score})
    def handledir(self,tmp , message , scoremessage):
        print(scoremessage.chat.id)
        if tmp in ["R", "r", "L", "l", "U", "u", "D", "d", "X", "x"]:
            dir = self.direction[tmp.upper()]
            if dir == 4:
                bot.send_message(message.chat.id , "\nFinal score: " + str(self.scoreOfAccs[message.chat.id]))
                self.gridOfAccs[message.chat.id] = []
            else:
                
                self.gridOfAccs[scoremessage.chat.id] = self.move(self.gridOfAccs[message.chat.id], dir , message)
                self.gridOfAccs[scoremessage.chat.id], self.loseOfAccs[message.chat.id] = self.addNumber(self.gridOfAccs[scoremessage.chat.id])
                self.printGrid(self.gridOfAccs[scoremessage.chat.id] , scoremessage.chat.id  , True , self.loseOfAccs[message.chat.id])
                scoretoshow = "score: " + str(self.scoreOfAccs[message.chat.id]) 
                if  scoretoshow != scoremessage.text:
                    try:
                        bot.edit_message_text(chat_id = scoremessage.chat.id, message_id = scoremessage.message_id, text= scoretoshow)
                    except:
                        print("exception exceeded")



playerbot = bot()
bot = playerbot.bot

@bot.message_handler(commands=['hello'])
def helloResponse(message):
  bot.reply_to(message, "hello dear!")
@bot.message_handler(commands=['start'])
def startBot(message):
  bot.reply_to(message, "welcome to abbuchy's 2048 , use \"/game\" to start the game.")

@bot.message_handler(commands = ['kir'  , 'fohsh'])
def deleteFohshs(message):
  bot.delete_message(message.chat.id ,  message.message_id, 1)
@bot.message_handler(commands = ['game'])
def startGameBot(message):    
  playerbot.startGame(message)
@bot.message_handler(commands = ['R' , 'U' , 'D' , 'L' , 'X'])
def editTemp(message):
  tmp = message.text[1:]
  playerbot.handledir(tmp , message , playerbot.scoremessageOfAccs[message.chat.id])
@bot.message_handler()
def handledirections(message):
  if(message.text == "Up"):
      bot.delete_message(message.chat.id ,  message.message_id, 1)
     
      playerbot.handledir("U" , message,playerbot.scoremessageOfAccs[message.chat.id])
 
  elif(message.text == "Down"):
      bot.delete_message(message.chat.id ,  message.message_id, 1)
      try:
          playerbot.handledir("D" , message,playerbot.scoremessageOfAccs[message.chat.id])
          print(playerbot.scoremessageOfAccs)
          print(playerbot.gridOfAccs)
      except:
          print("bad time handledir.")
  elif(message.text == "Right"):
      bot.delete_message(message.chat.id ,  message.message_id, 1)
      try:
          playerbot.handledir("R" , message,playerbot.scoremessageOfAccs[message.chat.id])
      except:
          print("bad time handledir.")
  elif(message.text == "Left"):
      bot.delete_message(message.chat.id ,  message.message_id, 1)
      try:
          playerbot.handledir("L" , message,playerbot.scoremessageOfAccs[message.chat.id])
      except:
          print("bad time handledir.")
  else:
      bot.reply_to(message, "?")

bot.polling()