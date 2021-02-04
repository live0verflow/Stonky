#!/usr/bin/env python

import os
import requests
from datetime import date, timedelta
from pretty_help import PrettyHelp
from pandas_datareader import data as pdr
from tradingview_ta import TA_Handler, Interval, Exchange
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as col
import robin_stocks as r
import yfinance as yf
import pandas as pd

import discord
from discord.ext import commands
from dotenv import load_dotenv

week_ago = date.today() - timedelta(7)
current_date = date.today() + timedelta(1)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="$", help_command=PrettyHelp())


#client = discord.Client()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(ctx):
	# we do not want the bot to reply to itself
	if ctx.author == bot.user:
		   return


	await bot.process_commands(ctx)

@bot.command()
async def stock(ctx, stock_name):
	"""Gives data for the past week of a stock"""
	try:
		data = yf.download(str(stock_name), start=str(week_ago), end=str(current_date))
	except:
		return
	if data.empty:
		return
	else:
		await ctx.send("```" + str(data.tail()) + "```")

@bot.command()
async def recom(ctx, stock_name):
	"""Shows what you should do with a stock, buy or sell"""
	"""try:
		ticker = yf.Ticker(str(stock_name))
		rec = pd.DataFrame(ticker.recommendations)
	except:
		return
	await ctx.send("```" + str(rec.tail(1)) + "```")"""
	try:
		handler = TA_Handler(
			symbol=str(stock_name),
			screener="america",
			exchange="NASDAQ",
			interval=Interval.INTERVAL_1_DAY
		)
		analysis = handler.get_analysis()
	except:
		try:
			handler = TA_Handler(
				symbol=str(stock_name),
				screener="america",
				exchange="NYSE",
				interval=Interval.INTERVAL_1_DAY
			)
			analysis = handler.get_analysis()
		except:
			try:

				handler = TA_Handler(
					symbol=str(stock_name),
					screener="crypto",
					exchange="binance",
					interval=Interval.INTERVAL_1_DAY
				)
				analysis = handler.get_analysis()
			except:
				return
	await ctx.send("```You should {0} {1} right NOW!```".format(analysis.summary['RECOMMENDATION'], stock_name))


@bot.command()
async def graph(ctx, stock_name, rang):
	"""shows a graph for the stock"""
	yf.pdr_override()
	try:
		if int(rang) > 7:
			stk = pdr.get_data_yahoo(tickers=str(stock_name), period= str(rang) + "d", interval="1d", auto_adjust=True, threads=True)
		else:
			stk = pdr.get_data_yahoo(tickers=str(stock_name), period= str(rang) + "d", interval="15m", auto_adjust=True, threads=True)
		if stk.empty:
			return
		else:
			fig = px.line(stk, y='High', title=str(stock_name))
			fig.write_image("./graph.png")
			await ctx.send(file=discord.File("graph.png"))
			os.remove("graph.png")
	except:
		return

@bot.command()
async def price(ctx, stock_name):
	"""Shows the current price of the stock"""
	try:
		ticker_yahoo = yf.Ticker(stock_name)
	except:
		return
	data = ticker_yahoo.history()
	last_quote = (data.tail(1)['Close'].iloc[0])
	await ctx.send("```" + str(last_quote) + "```")


bot.run(TOKEN)
