#!/usr/bin/env python

import os
import requests
from datetime import date, timedelta
from pretty_help import PrettyHelp
import plotly.graph_objects as go
import plotly.express as px
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
	"""Shows what different firms say about the stock"""
	try:
		ticker = yf.Ticker(str(stock_name))
		rec = pd.DataFrame(ticker.recommendations)
	except:
		return
	await ctx.send("```" + str(rec.tail(1)) + "```")

@bot.command()
async def graph(ctx, stock_name, rang):
	"""shows a graph for the stock"""
	try:
		stk = yf.Ticker(str(stock_name))
		df = stk.history(period="max")
		df = df.reset_index()
		for i in ['Open', 'High', 'Close', 'Low']:
			df[i] = df[i].astype('float64')
		if int(rang) > 0 or int(rang) < 10000:
			fig = px.line(df, x='Date', y='High', range_x=[str(date.today() - timedelta(int(rang))), str(date.today())])
			fig.write_image("./graph.png")
			await ctx.send(file=discord.File("graph.png"))
			os.remove("graph.png")
	except:
		return

bot.run(TOKEN)
