import io
import logging
import os
import shutil
import datetime
import pytz
from webserver import keep_alive
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from fpdf import FPDF

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)

TOKEN = "6227870277:AAGPAW51_rAR_ydE4VVhEsyDG7iAq0MOuGg"

last_text = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  allowed_ids = [158042764, 505592803]
  if (user_id not in allowed_ids):
    await update.message.reply_text(
      text="*Non hai il permesso di utilizzare questo bot!*",
      parse_mode='Markdown')
  else:
    keyboard = InlineKeyboardMarkup([[
      InlineKeyboardButton("Download ultimo rapporto📥",
                           callback_data="send_pdf")
    ]])
    await update.message.reply_text(
      text=
      f"*Ciao {update.effective_user.first_name}!*\nInviami i dati separati da una virgola nel formato `oggetto:quantità:taglia` e io creerò il pdf al posto tuo.\nSe l'oggetto non ha bisogno di una taglia specificata sarà sufficiente utilizzare la sintassi `oggetto:quantità`.\n\nQuesto bot è stato fatto per il solo utilizzo del reparto di *antincendio boschivo* di Migliarino.\nSviluppato con amore da @gioeleali per @maraMeo01🤝",
      parse_mode='Markdown',
      reply_markup=keyboard)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  user_id = query.from_user.id
  allowed_ids = [158042764, 505592803]
  if (user_id not in allowed_ids):
    await query.answer(
      text="Non hai il permesso di utilizzare questo comando!",
      show_alert=True)
  else:
    if query.data == "send_pdf":
      file_text = "pdf/code.txt"
      if os.path.isfile(file_text):
        with open(file_text, "r", encoding="utf-8") as file:
          last_text_content = file.read()
      file_path = "pdf/materiale-aib.pdf"
      if os.path.isfile(file_path):
        bot = Bot(token=TOKEN)
        with open(file_path, "rb") as file:
          await query.message.reply_document(
            document=file,
            caption=f"*Ultimo rapporto:*\n`{last_text_content}`",
            parse_mode='Markdown')
      else:
        await query.answer(text="Nessun PDF disponibile!❌")


async def crea_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global last_text
  user_id = update.effective_user.id
  allowed_ids = [158042764, 505592803]
  if (user_id not in allowed_ids):
    await update.message.reply_text(
      text="*Non hai il permesso di utilizzare questo bot!*",
      parse_mode='Markdown')
  else:
    text = update.message.text.strip()
    last_text = text
    items = text.split(',')
    data = []
    for item in items:
      parts = item.strip().split(':')
      if len(parts) == 3:
        oggetto = parts[0].strip().capitalize()
        quantita = parts[1].strip()
        taglia = parts[2].strip().upper()
        data.append([oggetto, quantita, taglia])
      elif len(parts) == 2:
        oggetto = parts[0].strip().capitalize()
        quantita = parts[1].strip()
        data.append([oggetto, quantita, "/"])
      else:
        await update.message.reply_text(
          text=
          "*Formato errato!*\nAssicurati di utilizzare il formato `oggetto:quantita:taglia` o `oggetto:quantita`.",
          parse_mode='Markdown')
        return
    pdf = FPDF()
    pdf.add_page()
    image_path = 'pa.png'
    pdf.image(image_path, x=20, y=5, w=20)
    image_path = 'anpas.png'
    pdf.image(image_path, x=160, y=5, w=30)
    pdf.ln()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Materiale AIB", ln=True, align='C')
    pdf.set_y(15)
    pdf.set_font("Arial", style="I", size=8)
    now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
    datetime_str = now.strftime("%d/%m/%Y alle %H:%M")
    pdf.cell(0,
             10,
             txt=f"Ultimo aggiornamento il {datetime_str}",
             ln=True,
             align='C')
    page_width = pdf.w - 2 * pdf.l_margin
    table_width = 60 * 3
    table_x = pdf.l_margin + (page_width - table_width) / 2
    pdf.set_font("Arial", style="B", size=12)
    pdf.set_x(table_x)
    pdf.cell(60, 10, txt="Oggetti", border=1, align='C')
    pdf.cell(60, 10, txt="Quantità", border=1, align='C')
    pdf.cell(60, 10, txt="Taglie", border=1, align='C')
    pdf.ln()
    pdf.set_font("Arial", size=12)
    color1 = 255
    color2 = 230
    i = 0
    for item in data:
      if i % 2 == 0:
        pdf.set_fill_color(color1)
        i += 1
      else:
        pdf.set_fill_color(color2)
        i += 1
      pdf.set_x(table_x)
      pdf.cell(60, 10, txt=item[0], border=1, fill=True)
      pdf.cell(60, 10, txt=item[1], border=1, align='C', fill=True)
      pdf.cell(60, 10, txt=item[2], border=1, align='C', fill=True)
      pdf.ln()
    pdf_filename = 'materiale-aib.pdf'
    pdf.output(pdf_filename)
    destination_path = 'pdf/materiale-aib.pdf'
    shutil.copy(pdf_filename, destination_path)
    with open(pdf_filename, 'rb') as pdf_file:
      await update.message.reply_document(
        document=pdf_file,
        caption=f"*Materiale AIB del {datetime_str}*",
        parse_mode='Markdown')
    os.remove(pdf_filename)
    file_path = "pdf/code.txt"
    with io.open(file_path, "w", encoding="utf-8") as file:
      file.write(last_text)


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  if (user_id == 158042764):
    bot = Bot(token=TOKEN)
    users = set()
    updates = await bot.get_updates(offset=-1)
    for update in updates:
      user = update.message.from_user
      users.add(user.id)
    await update.message.reply_text(text=f"Numero di utenti: *{len(users)}*",
                                    parse_mode='Markdown')


keep_alive()
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('users', users))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT, crea_pdf))
print("Loading...")
app.run_polling()
app.idle()
