import telebot, os, dotenv, queue, threading, time, yt_dlp

dotenv.load_dotenv()
bot=telebot.TeleBot(os.getenv('token'))
fila_download=queue.Queue()
threads=int(os.getenv('threads'))
path_files=os.getenv('path')
comandos=[
	telebot.types.BotCommand(command="start",description="Conhecer o bot"),
	telebot.types.BotCommand(command="yt_dv",description="Para baixar video /yt_dv [url]"),
	telebot.types.BotCommand(command="yt_da",description="Para baixar audio /yt_da [url]"),
	telebot.types.BotCommand(command="contato",description="Para entrar em contato com o dev")
]

bot.set_my_commands(comandos)

@bot.message_handler(commands=['start'])
def bem_vindo_bot(mensagem):
	bot.reply_to(mensagem,f"🧝🏼‍♀️ Olá, eu sou a {os.getenv('nome')}!\nE um prazer em te conhecer 🤝.")
	
@bot.message_handler(commands=['yt_dv'])
def download(mensagem):
	partes=(mensagem.text).split(" ")
	if(len(partes) >= 2):
		url=partes[1]
		if(('youtube.com' in url) or ('youtu.be' in url)):
			fila_download.put((mensagem, url,"video"))
			bot.reply_to(mensagem,f'✅ Pedido recebido\n🔗 Link: {url[:40]}\n🕔 Na fila atual: {fila_download.qsize()}')
		else:
			bot.reply_to(mensagem,'Precisa ter um link valido do youtube!')
	else:
		bot.reply_to(mensagem,'Precisa passar o link!')

@bot.message_handler(commands=['yt_da'])
def download(mensagem):
	partes=(mensagem.text).split(" ")
	if(len(partes) >= 2):
		url=partes[1]
		if(('youtube.com' in url) or ('youtu.be' in url)):
			fila_download.put((mensagem, url,"audio"))
			bot.reply_to(mensagem,f'✅ Pedido recebido\n🔗 Link: {url[:40]}\n🕔 Na fila atual: {fila_download.qsize()}')
		else:
			bot.reply_to(mensagem,'Precisa ter um link valido do youtube!')
	else:
		bot.reply_to(mensagem,'Precisa passar o link!')

@bot.message_handler(commands=['contato'])
def contato(mensagem):
	bot.reply_to(mensagem,f"Contato para falar com o desenvolvedor: {os.getenv("contato")}")
	
def thread_download(thread_id):
	print(f"Iniciando a thread: {thread_id}")
	while True:
		task=fila_download.get()
		if (task is not None):
			time.sleep(1)
			mensagem, url, tipo = task
			if(tipo == "video"):
				bot.reply_to(mensagem,f"⚙️ A thread {thread_id}, está processando o seu video...")
				nome_arquivo=f'{path_files}video_{mensagem.message_id}.mp4'
				ydl_opts={
					'format':'bestvideo[height<=720]+bestaudio/best[height<=720]', #Para baixar na melhor resolução possivel usar 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
					'outtmpl':nome_arquivo,
					'merge_output_format':'mp4'
				}
				print(f'thread {thread_id} processando ')
				with yt_dlp.YoutubeDL(ydl_opts) as ydl:
					ydl.download(url)
				if((os.path.getsize(nome_arquivo)/(1024*1024)) <= 50):
					with open(nome_arquivo,'rb') as video_file:
						try:
							bot.send_video(mensagem.chat.id,video_file,caption=f'🎬 Arquvo baixado com sucesso!')
						except:
							bot.send_document(mensagem.chat.id,video_file,caption=f'🎬 Arquvo baixado com sucesso!')
				else:
					bot.reply_to(mensagem,"❌ Infelistmente o seu arquivo tem mais de 50 MB, eu só posso mandar até 50 MB")
				if(os.path.exists(nome_arquivo)):
					os.remove(nome_arquivo)
				else:
					pass
				bot.reply_to(mensagem,"Ajudo em mais alguma coisa!")
			elif(tipo == "audio"):
				bot.reply_to(mensagem,f"⚙️ A thread {thread_id}, está processando o seu audio...")
				nome_arquivo=f'{path_files}video_{mensagem.message_id}.mp3'
				ydl_opts={
					'format': 'bestaudio/best',
					'postprocessors': [{
						'key': 'FFmpegExtractAudio',
						'preferredcodec': 'mp3',
						'preferredquality': '192',
					}],
					'outtmpl': nome_arquivo.replace(".mp3",""),
				}
				with yt_dlp.YoutubeDL(ydl_opts) as ydl:
					ydl.download(url)
				if((os.path.getsize(nome_arquivo)/(1024*1024)) <= 50):
					with open(nome_arquivo,'rb') as audio_file:
						try:
							bot.send_audio(mensagem.chat.id,audio_file,caption=f'🎵 Arquvo baixado com sucesso!')
						except:
							bot.send_document(mensagem.chat.id,audio_file,caption=f'🎵 Arquvo baixado com sucesso!')
				else:
					bot.reply_to(mensagem,"❌ Infelistmente o seu arquivo tem mais de 50 MB, eu só posso mandar até 50 MB")
				if(os.path.exists(nome_arquivo)):
					os.remove(nome_arquivo)
				else:
					pass
				bot.reply_to(mensagem,"Ajudo em mais alguma coisa!")
			else:
				bot.reply_to(mensagem,"Tipo invaido!")
		else:
			time.sleep(10)
			
for c in range(0,threads):
	t = threading.Thread(target=thread_download,args=(c,),daemon=True)
	t.start()

print("Iniciando bot")
bot.infinity_polling()
