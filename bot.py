#!/usr/bin/env python3
#remember to pip install kaleido
#miscellaneous imports
import os
import asyncio
import requests

#only needed a few things from here
from datetime import date, timedelta
from pretty_help import PrettyHelp
from dotenv import load_dotenv
from pandas_datareader import data as pdr
from tradingview_ta import TA_Handler, Interval, Exchange

#most of the finance libs are here in full a few pieces are above
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as col
import robin_stocks as r
import cryptoapi as cr
import yfinance as yf
import pandas as pd

#import neccesary discord libs
import discord
from discord.ext import commands

#used to get proper dates for certain time sensitive commands
week_ago = date.today() - timedelta(7)
current_date = date.today() + timedelta(1)

#initialization of the environment to run the bot
#load_dotenv()
#f = open("/root/token", "r")
f = open("../secret", "r")
TOKEN = f.readline()
bot = commands.Bot(command_prefix="$", help_command=PrettyHelp())


#client = discord.Client()

@bot.event
async def on_ready(): #this finction will run when the bot has succesfully connected
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(ctx):
	# we do not want the bot to reply to itself
	if ctx.author == bot.user:
		   return


	await bot.process_commands(ctx) #bot is awaiting commands

@bot.command()
async def stock(ctx, stock_name):
	"""Gives data for the past week of a stock"""
	try:
		data = yf.download(str(stock_name), start=str(week_ago), end=str(current_date)) #download the data from the past week
	except:
		return
	if data.empty: #if the data is empty something went wrong, end function
		return
	else:
		await ctx.send("```" + str(data.tail()) + "```") #send data formatted to the user

@bot.command()
async def recom(ctx, stock_name):
	"""Shows what you should do with a stock, buy or sell"""
	"""try:
		ticker = yf.Ticker(str(stock_name))
		rec = pd.DataFrame(ticker.recommendations)
	except:
		return
	await ctx.send("```" + str(rec.tail(1)) + "```")"""
	try: #see if the stock is in NASDAQ
		handler = TA_Handler(
			symbol=str(stock_name),
			screener="america",
			exchange="NASDAQ",
			interval=Interval.INTERVAL_1_DAY
		)
		analysis = handler.get_analysis() #get the analysis of the stock
	except:
		try: #see if the stock is in the NYSE
			handler = TA_Handler(
				symbol=str(stock_name),
				screener="america",
				exchange="NYSE",
				interval=Interval.INTERVAL_1_DAY
			)
			analysis = handler.get_analysis()
		except:
			try: #else check if its a crypto

				handler = TA_Handler(
					symbol=str(stock_name),
					screener="crypto",
					exchange="binance",
					interval=Interval.INTERVAL_1_DAY
				)
				analysis = handler.get_analysis()
			except:
				return #if none of the above end the function
	await ctx.send("```You should {0} {1} right NOW!```".format(''.join(analysis.summary['RECOMMENDATION'].replace('_', ' ')), stock_name)) #tells the user what they should do with the stock or crypto


@bot.command()
async def graph(ctx, stock_name, rang):
	"""shows a graph for the stock"""
	yf.pdr_override() #use pandas data frame instead of yfinance format
	if int(rang) > 7: #if the user specified a time period greater than a week update every day
		stk = pdr.get_data_yahoo(tickers=str(stock_name), period= str(rang) + "d", interval="1d", auto_adjust=True, threads=True)
	elif int(rang) <= 7 and int(rang) > 0: #less than a week every 15 minutes
		stk = pdr.get_data_yahoo(tickers=str(stock_name), period= str(rang) + "d", interval="15m", auto_adjust=True, threads=True)
	if stk.empty: #no stock specified; end
		return
	else:
		fig = px.line(stk, y='High', title=str(stock_name)) #generate a stock graph from user specified constraints
		fig.write_image("./graph.png") #generate image and send
		await ctx.send(file=discord.File("graph.png"))
		os.remove("graph.png") #delete image
	return

@bot.command()
async def price(ctx, stock_name):
	"""Shows the current price of the stock"""
	try:
		#try to get the ticker data if can't because bad name or other error return and end function
		ticker_yahoo = yf.Ticker(stock_name)
	except:
		return
	data = ticker_yahoo.history() #get the histroy of the stock from the ticker
	last_quote = (data.tail(1)['Close'].iloc[0]) #get the most recent quote price
	await ctx.send("```" + str(last_quote) + "```") #send the price to the server

@bot.command()
async def alert(ctx, name, pos, price):
	"""alerts a user of a price change in a stock"""
	try:
		#if the user wants the price when it falls under a certain price try this
		if str(pos) == "under":
			while True:
				stk = yf.Ticker(str(name)) #get stock data from yahoo
				data = stk.history() #get the history of the stock
				last_quote = (data.tail(1)['Close'].iloc[0]) #what is the most recent price
				if int(last_quote) < int(price): #if the recent price is less than the price specified in the invocation
					await ctx.send("{} is {} {} {}".format(str(name), str(pos), str(price), ctx.author.mention)) #send alert to user that invoked the command
					break
				await asyncio.sleep(300) #dont DOS yfinance or pin my CPU
		elif str(pos) =="over":
			#if the user wants the price when it goes over a certain price do this
			while True:
				stk = yf.Ticker(str(name))
				data = stk.history()
				last_quote = (data.tail(1)['Close'].iloc[0])
				if int(last_quote) > int(price):
					await ctx.send("{} is {} {} {}".format(str(name), str(pos), str(price), ctx.author.mention))
					break
				await asyncio.sleep(300)
		else:
			await ctx.send("please follow the format") #they didnt follow the format, dummies
	except:
		return


@bot.command()
async def cheat(ctx, lang, *query):

    if lang == "help":
        r = requests.get("https://cht.sh/" + ":" + lang)
        if r.status_code == 200:
            h = r.text[600:]
            await ctx.send("```" + str(h) + "```")
    else:
        r = requests.get("https://cht.sh/" + lang + "/{}".format("+".join(query)) + "?QT")
        print(r.text)
        if r.status_code == 200:
            await ctx.send("```" + str(lang) + "\n"+ str(r.text) + "```")

bot.run(TOKEN)
