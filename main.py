from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import time
import requests
import datetime
from time import sleep
import random
import hashlib
from asyncio import sleep as asyncio_sleep
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from commands import *
import os
from PIL import Image

api_id = 24679387
api_hash = "ad9e119acbfc9de527e1da32fae2a866"
plugins = dict(root="modules")

ALLOWED_USERS = [7271527237, 5977658793]  # Ganti dengan user ID Telegram Anda

# Variabel untuk menyimpan waktu awal bot mulai
start_time = time.time()

# Mode default
mode = 2

# Daftar bendera dengan detail negara
flags = {
    "🇮🇩": "Indonesia",
    "🇺🇸": "Amerika Serikat",
    "🇯🇵": "Jepang",
    "🇫🇷": "Perancis",
    "🇧🇷": "Brasil",
    "🇬🇧": "Inggris",
    "🇨🇦": "Kanada",
    "🇮🇹": "Italia",
    "🇩🇪": "Jerman",
    "🇦🇺": "Australia",
    "🇪🇸": "Spanyol",
    "🇨🇳": "Cina",
    "🇷🇺": "Rusia",
    "🇰🇷": "Korea Selatan",
    "🇸🇦": "Arab Saudi",
    "🇲🇽": "Meksiko",
    "🇳🇱": "Belanda",
    "🇨🇭": "Swiss",
    "🇦🇷": "Argentina",
    "🇿🇦": "Afrika Selatan",
    "🇳🇴": "Norwegia",
    "🇸🇪": "Swedia",
    "🇮🇳": "India",
    "🇧🇪": "Belgia",
    "🇪🇬": "Mesir",
    "🇹🇷": "Turki",
    "🇵🇹": "Portugal",
    "🇮🇱": "Israel",
    "🇳🇬": "Nigeria",
    "🇦🇪": "Uni Emirat Arab",
    # Tambahkan lebih banyak bendera dan negara di sini jika diperlukan
}

with Client("my_account", api_id=api_id, api_hash=api_hash, plugins=plugins) as app:
    app.send_message("me", 'bot dinyalakan')
    print('dinyalakan')

    @app.on_inline_query()
    async def inline_tebak_bendera(client, inline_query):
        bendera, negara = random.choice(list(flags.items()))

        # Create a unique ID using hashlib
        result_id = hashlib.md5(bendera.encode()).hexdigest()

        # Generate an inline keyboard with the options for the user to guess
        options = list(flags.values())
        random.shuffle(options)

        keyboard = [[InlineKeyboardButton(option, callback_data=f"guess_{option}")] for option in options]

        results = [
            InlineQueryResultArticle(
                id=result_id,
                title="Tebak Bendera",
                input_message_content=InputTextMessageContent(f"Tebak bendera ini: {bendera}\nPilih jawabanmu dari tombol di bawah!"),
                reply_markup=InlineKeyboardMarkup(keyboard),
                description="Klik untuk bermain tebak bendera",
            )
        ]

        await client.answer_inline_query(inline_query.id, results, cache_time=0)

    @app.on_message(filters.command("tebakbendera"))
    async def command_tebak_bendera(client, message):
        bendera, negara = random.choice(list(flags.items()))

        options = list(flags.values())
        random.shuffle(options)

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(option, callback_data=f"guess_{option}")] for option in options]
        )

        await message.reply(
            f"Tebak bendera ini: {bendera}\nPilih jawabanmu dari tombol di bawah!",
            reply_markup=keyboard
        )

    @app.on_callback_query()
    async def handle_guess(client, callback_query):
        guess = callback_query.data.split("_")[1]
        correct_flag = next((flag for flag, country in flags.items() if country == guess), None)

        if correct_flag:
            await callback_query.answer(f"Selamat! Jawabanmu benar. Bendera ini adalah {guess}.", show_alert=True)
        else:
            await callback_query.answer("Jawaban salah. Coba lagi!", show_alert=True)

    games = {}

    def get_board_markup(board):
        buttons = []
        for row in range(3):
            button_row = []
            for col in range(3):
                button_text = board[row][col]
                button_data = f"{row}{col}"
                button_row.append(InlineKeyboardButton(button_text, callback_data=button_data))
            buttons.append(button_row)
        return InlineKeyboardMarkup(buttons)

    def check_winner(board):
        for row in board:
            if row[0] == row[1] == row[2] and row[0] != " ":
                return row[0]
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] and board[0][col] != " ":
                return board[0][col]
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != " ":
            return board[0][2]
        return None

    def is_full(board):
        for row in board:
            for cell in row:
                if cell == " ":
                    return False
        return True

    @app.on_message(filters.command("tictactoe", prefixes="."))
    async def start_tictactoe(client, message):
        chat_id = message.chat.id
        games[chat_id] = {
            "board": [[" " for _ in range(3)] for _ in range(3)],
            "turn": "X"
        }
        await message.reply("Tic-Tac-Toe game started!\nPlayer X's turn.", reply_markup=get_board_markup(games[chat_id]["board"]))

    @app.on_callback_query()
    async def handle_turn(client, callback_query):
        chat_id = callback_query.message.chat.id
        if chat_id not in games:
            await callback_query.answer("No game in progress.", show_alert=True)
            return

        game = games[chat_id]
        board = game["board"]
        turn = game["turn"]

        row, col = int(callback_query.data[0]), int(callback_query.data[1])

        if board[row][col] != " ":
            await callback_query.answer("Invalid move! Cell already taken.", show_alert=True)
            return

        board[row][col] = turn
        winner = check_winner(board)
        if winner:
            await callback_query.message.edit_text(f"Player {winner} wins!", reply_markup=get_board_markup(board))
            del games[chat_id]
        elif is_full(board):
            await callback_query.message.edit_text("It's a draw!", reply_markup=get_board_markup(board))
            del games[chat_id]
        else:
            game["turn"] = "O" if turn == "X" else "X"
            await callback_query.message.edit_text(f"Player {game['turn']}'s turn.", reply_markup=get_board_markup(board))

        await callback_query.answer()

    def is_allowed(user_id):
        return user_id in ALLOWED_USERS

    @app.on_message(filters.command("ping", prefixes=".") & filters.me)
    async def ping_pong(client, message):
        if not is_allowed(message.from_user.id):
            await message.reply_text("You are not authorized to use this command.")
            return

        start = time.time()
        msg = await message.reply_text("Pong!")
        end = time.time()
        await msg.edit_text(f"Pong! {round((end - start) * 1000)}ms")

    @app.on_message(filters.command("alive", prefixes=".") & filters.me)
    async def alive(client, message):
        if not is_allowed(message.from_user.id):
            await message.reply_text("You are not authorized to use this command.")
            return

        uptime = time.time() - start_time
        uptime_str = str(datetime.timedelta(seconds=int(uptime)))
        start_time_str = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        await message.reply_text(f"Bot has been running for: {uptime_str}\nStarted at: {start_time_str}")

    @app.on_message(filters.command("mode", prefixes=".") & filters.group & filters.me)
    async def set_mode(client, message):
        if not is_allowed(message.from_user.id):
            await message.reply_text("You are not authorized to use this command.")
            return

        try:
            new_mode = int(message.text.split(" ", 1)[1])
            global mode

            if new_mode in [1, 2]:
                mode = new_mode
                if mode == 1:
                    await client.set_chat_description(message.chat.id, "ISeven playing a game!")
                else:
                    await client.set_chat_description(message.chat.id, "")
                await message.reply_text(f"Mode has been set to: {mode}")
            else:
                await message.reply_text("Invalid mode! Please choose between 1 and 2.")
        except (IndexError, ValueError):
            await message.reply_text("Invalid mode! Please choose between 1 and 2.")

    @app.on_message(filters.command("exec", prefixes="."))
    async def exec_shell_command(client, message):
        # Memeriksa apakah user ID pengirim ada dalam daftar yang diizinkan
        if message.from_user.id not in ALLOWED_USERS:
            await message.reply_text("You are not authorized to use this command.")
            return

        try:
            # Mendapatkan perintah dari pesan (menghilangkan prefix dan command)
            command = message.text.split(" ", 1)[1]

            # Menjalankan perintah shell
            result = os.popen(command).read()

            # Mengirimkan hasil eksekusi kembali ke chat dengan Markdown
            await message.reply_text(f"**Command:**\n```\n{command}\n```\n\n**Result:**\n```\n{result}\n```")
        except IndexError:
            await message.reply_text("Please provide a command to execute.")
        except Exception as e:
            await message.reply_text(f"An error occurred: ```\n{e}\n```")

    @app.on_message(filters.command('run', prefixes=['.', '/', '!']) & filters.me)
    def run(client, message):
        expression = message.text.split(None, 1)[1]
        try:
            result = eval(expression)
        except Exception as e:
            message.reply_text(f"Error executing:\n{e}")

    def rgb_to_hex(r, g, b):
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return hex_color

    @app.on_message(filters.command('colorhex') & filters.me)
    async def colorhex(_, msg):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        width, height = 256, 256
        colorHex = rgb_to_hex(r, g, b)
        color = r, g, b
        color_image = Image.new('RGB', (width, height), color)
        color_image.save('color_image.jpg')
        await app.send_photo(msg.chat.id,
                             'color_image.jpg',
                             caption=f'<code>{colorHex}</code>')

    @app.on_message(filters.command('color') & filters.me)
    async def color(_, msg):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        width, height = 256, 256
        color = r, g, b
        color_image = Image.new('RGB', (width, height), color)
        color_image.save('color_image.jpg')
        await app.send_photo(msg.chat.id,
                             'color_image.jpg',
                             caption=f'<code>{r}, {g}, {b}</code>')
        os.remove('color_image.jpg')
        print(rgb_to_hex(r, g, b))

    @app.on_message(filters.command('random_member', prefixes=['/', '.']))
    async def rand(_, message):
        chat_members = await app.get_chat_members(message.chat.id)
        random_user = random.choice(chat_members)
        print(f'User Name: {random_user.user.first_name}')
        print(f'User ID: {random_user.user.id}')

    @app.on_message(filters.command("t1", ".") & filters.me)
    async def type1(_, msg):
        orig_text = msg.text.split(".t1 ", maxsplit=1)[1]
        text = orig_text
        tbp = ""
        typing_symbol = "▒"

        while tbp != orig_text:
            try:
                await msg.edit(tbp + typing_symbol)
                await asyncio_sleep(0.05)

                tbp = tbp + text[0]
                text = text[1:]

                await msg.edit(tbp)
                await asyncio_sleep(0.05)
                
            except FloodWait as e:
                 await asyncio_sleep(e.x)
                
    @app.on_message(filters.command("t2", prefixes=".") & filters.me)
    async def type2(_, msg):
        orig_text = msg.text.split(".t2 ", maxsplit=1)[1]
        text = orig_text
        tbp = ""
        typing_symbol = "❤"

        while tbp != orig_text:
            try:
                await msg.edit(tbp + typing_symbol)
                await asyncio_sleep(0.05)

                tbp = tbp + text[0]
                text = text[1:]

                await msg.edit(tbp)
                await asyncio_sleep(0.05)
                
            except FloodWait as e: 
                await asyncio_sleep(e.x)

app.run()
