import os
import discord
import googletrans
#pip install googletrans==3.1.0a0
from googletrans import Translator
from discord.ext import commands
import requests
import json
import hanzidentifier


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
client = discord.Client(intents=intents)

translator = Translator(service_urls=['translate.googleapis.com'])


@bot.command(help="fonction test",
             description="Répond bonjour avec le nom de l'utilisateur")
async def bonjour(ctx):
  await ctx.send(f"Bonjour {ctx.author} !")


@bot.command()
async def aurevoir(ctx, test):
  await ctx.send(f"Aurevoir {test} {ctx.author} !")


@bot.command(aliases=['tr'])
async def translate_sentence(ctx, lang_to, *args):
  """
    Translates the given text to the language `lang_to`.
    The language translated from is automatically detected.
    """

  lang_to = lang_to.lower()
  if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
    raise commands.BadArgument("Invalid language to translate text to")

  text = ' '.join(args)
  translator = googletrans.Translator()
  text_translated = translator.translate(text, dest=lang_to).text
  await ctx.send(text_translated)


@bot.command(aliases=['trad'])
async def translate(ctx, lang_to, arg):

  lang_to = lang_to.lower()
  if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
    raise commands.BadArgument("Invalid language to translate text to")

  
  translator = googletrans.Translator()

  text_translated = translator.translate(arg, dest=lang_to).text

  await ctx.send(f"{arg} in {lang_to} means **{text_translated}**")
  """
    Trad en chinois
  """
  trad_china = translator.translate(arg, dest='zh-tw').text
  src = translator.translate(arg, dest='zh-tw').src

  table_china = [*trad_china]
  await ctx.send(f"Hanja : **{trad_china}**")

  for kanji in table_china:
    trad_kanji_en = translator.translate(kanji, dest='en').text
    trad_kanji_kr = translator.translate(kanji, dest='ko').text
    await ctx.send(f"{kanji} => {trad_kanji_en} => {trad_kanji_kr}")
  """
    Fin trad en chinois
  """

  src_url = ""
  if src == "fr":
    src_url = "fra"
  if src == "en":
    src_url = "eng"
  if src == "ko":
    src_url = "kor"

  dest_url = ""
  if lang_to == "french":
    dest_url = "fra"
  if lang_to == "english":
    dest_url = "eng"
  if lang_to == "korean":
    dest_url = "kor"

  response = requests.get(
      f"https://api.dev.tatoeba.org/unstable/sentences?lang={src_url}&q={arg}&trans={dest_url}"
  )
  rep = response.json()

  await ctx.send("__**EXEMPLE :**__")

  if rep['data'] == []:
    await ctx.send("*No exemple found*")
  else:

    for sentence in rep['data']:
      if sentence['text'].find(arg):
        sentence['text'] = sentence['text'].replace(arg, f"**{arg}**")
      await ctx.send(f"Ex : original sentence =>  {sentence['text']}")
      if len(sentence['translations'][0]) == 0:
        for traduction in sentence['translations'][1]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"Translate sentence =>  {traduction['text']}")
      else:
        for traduction in sentence['translations'][0]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"Translate sentence =>  {traduction['text']}")

@bot.command(aliases=['ex'])
async def exemple(ctx, arg):

  text_translated = translator.translate(arg, dest="en").text
  src = translator.translate(arg, dest='en').src

  src_url = ""
  if src == "fr":
    src_url = "fra"
  if src == "en":
    src_url = "eng"
  if src == "ko":
    src_url = "kor"
  if src == "jp":
    src_url = "jpn"

  response = requests.get(
      f"https://api.dev.tatoeba.org/unstable/sentences?lang={src_url}&q={arg}&trans=eng"
  )

  rep = response.json()

  if rep['data'] == []:
    await ctx.send("*No exemple found*")
  else:

    for sentence in rep['data']:
      if sentence['text'].find(arg):
        sentence['text'] = sentence['text'].replace(arg, f"**{arg}**")
      await ctx.send(f"__Ex__ : {sentence['text']}")
      if len(sentence['translations'][0]) == 0:
        for traduction in sentence['translations'][1]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"*__Translation__ :  {traduction['text']}*")
      else:
        for traduction in sentence['translations'][0]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"*__Translation__ :  {traduction['text']}*")


@bot.command(aliases=['jp'])
async def jap(ctx, arg):

  #await ctx.send(hanzidentifier.has_chinese('パソコン'))

  src = translator.translate(arg, dest="fr").src
  text_translated = translator.translate(arg, dest="fr").text
  pronunciation = translator.translate(arg, dest="ja").pronunciation
  await ctx.send(f"{arg} (*{pronunciation}*) means **{text_translated}**")

  await ctx.send(" \n __**KANJI :**__ \n")
  
  table_china = [*arg]

  for kanji in table_china:
    #await ctx.send(f"{kanji} is a hanja ? {hanzidentifier.has_chinese(kanji)}")
    if hanzidentifier.has_chinese(kanji) == True:
      trad_kanji_en = translator.translate(kanji, dest='en').text
      trad_kanji_fr = translator.translate(kanji, dest='fr').text
      await ctx.send(f"{kanji} => {trad_kanji_en} => {trad_kanji_fr}")

  response = requests.get(
    f"https://api.dev.tatoeba.org/unstable/sentences?lang=jpn&q={arg}&trans=eng"
  )
  rep = response.json()

  await ctx.send(f"\n__**EXEMPLE(S) :**__ \n")
  
  if rep['data'] == []:
    await ctx.send("*No exemple found*")
  else:

    for sentence in rep['data']:
      if sentence['text'].find(arg):
        sentence['text'] = sentence['text'].replace(arg, f"**{arg}**")
      pronunce = translator.translate(sentence['text'], dest="ja").pronunciation
      await ctx.send(f"__Ex__ : {sentence['text']} (*{pronunce}*)")
      if len(sentence['translations'][0]) == 0:
        for traduction in sentence['translations'][1]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"*__Translation__ :  {traduction['text']}*")
      else:
        for traduction in sentence['translations'][0]:
          if traduction['text'].find(text_translated):
            traduction['text'] = traduction['text'].replace(
                text_translated, f"__{text_translated}__")
          await ctx.send(f"*__Translation__ :  {traduction['text']}*")
  
token = os.environ['TOKEN_BOT_TOKEN']

bot.run(token)
