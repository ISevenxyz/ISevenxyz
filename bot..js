const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs-extra');
const archiver = require('archiver');
const path = require('path');
const moment = require('moment');
const disk = require('diskusage');

// Token bot Telegram
const token = '7291179531:AAFlulaeGK3dEidFAnnYOFZsc3t0MpON8fw';

// Folder yang akan di-backup
const folderToBackup = './myfolder'; // Jalur relatif ke folder yang ingin di-backup

// Inisialisasi bot
const bot = new TelegramBot(token, { polling: true });

let gameData = {}; // Menyimpan data permainan untuk setiap pengguna

// Fungsi untuk membuat file zip dari folder
const createBackup = async (backupPath) => {
  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(backupPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      resolve(archive.pointer());
    });

    archive.on('error', err => {
      reject(err);
    });

    archive.pipe(output);
    archive.directory(folderToBackup, false);
    archive.finalize();
  });
};

// Fungsi untuk mengirim file zip ke pengguna
const sendBackup = async (chatId, backupPath) => {
  try {
    await bot.sendDocument(chatId, backupPath, {
      caption: 'Here is your backup file. @ISevennet My Owner'
    });
    console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Backup file sent to chat ID: ${chatId}`);
  } catch (error) {
    bot.sendMessage(chatId, `Failed to send backup file: ${error.message}`);
  }
};

// Fungsi untuk memeriksa penggunaan disk
const checkDiskUsage = async (chatId) => {
  try {
    const path = '/'; // Menentukan path root untuk pemeriksaan disk
    const { available, free, total } = await disk.check(path);
    const used = total - free;

    const message = `
Disk Usage:
Total: ${(total / 1024 / 1024 / 1024).toFixed(2)} GB
Used: ${(used / 1024 / 1024 / 1024).toFixed(2)} GB
Free: ${(free / 1024 / 1024 / 1024).toFixed(2)} GB
Available: ${(available / 1024 / 1024 / 1024).toFixed(2)} GB
    `;

    bot.sendMessage(chatId, message);
    console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Disk usage information sent to chat ID: ${chatId}`);
  } catch (error) {
    bot.sendMessage(chatId, `Failed to check disk usage: ${error.message}`);
    console.error(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Error checking disk usage: ${error.message}`);
  }
};

// Fungsi untuk memulai game Guess the Number
const startGame = (chatId) => {
  const randomNumber = Math.floor(Math.random() * 100) + 1;
  gameData[chatId] = { number: randomNumber, attempts: 0 };
  bot.sendMessage(chatId, 'I have picked a random number between 1 and 100. Can you guess it? Send your guess as a message.');
  console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Started Guess the Number game for chat ID: ${chatId}`);
};

// Fungsi untuk menangani tebakan dalam game
const handleGuess = (chatId, guess) => {
  const game = gameData[chatId];
  if (!game) {
    bot.sendMessage(chatId, 'Please start a new game by clicking the "Play Guess the Number" button.');
    return;
  }

  game.attempts += 1;
  if (guess < game.number) {
    bot.sendMessage(chatId, 'Too low! Try again.');
  } else if (guess > game.number) {
    bot.sendMessage(chatId, 'Too high! Try again.');
  } else {
    bot.sendMessage(chatId, `Congratulations! You guessed the number in ${game.attempts} attempts.`);
    console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Game won by chat ID: ${chatId} in ${game.attempts} attempts`);
    delete gameData[chatId]; // Menghapus data game setelah selesai
  }
};

// Menangani perintah /start
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const userName = msg.from.username || `${msg.from.first_name} ${msg.from.last_name}`;
  const timestamp = moment().format('YYYY-MM-DD HH:mm:ss');

  // Log ke konsol
  console.log(`[${timestamp}] Received /start command from ${userName} (chat ID: ${chatId})`);

  // Inline button untuk memulai backup, memeriksa penggunaan disk, dan bermain game
  const options = {
    reply_markup: {
      inline_keyboard: [
        [{ text: 'ʙᴀᴄᴋᴜᴘ', callback_data: 'create_backup' }],
        [{ text: 'ᴅɪsᴋ ᴄʜᴇᴄᴋ', callback_data: 'check_disk_usage' }],
        [{ text: 'ɢᴜᴇsᴛ ɴᴜᴍʙᴇʀ', callback_data: 'play_guess_the_number' }]
      ]
    }
  };

  bot.sendMessage(chatId, 'Welcome! Choose an option below: @ISevennet !', options);
});

// Menangani callback dari inline button
bot.on('callback_query', async (callbackQuery) => {
  const message = callbackQuery.message;
  const chatId = message.chat.id;
  const userName = callbackQuery.from.username || `${callbackQuery.from.first_name} ${callbackQuery.from.last_name}`;
  const timestamp = moment().format('YYYY-MM-DD HH:mm:ss');

  if (callbackQuery.data === 'create_backup') {
    bot.sendMessage(chatId, 'Creating backup, please wait...');
    console.log(`[${timestamp}] Backup creation started by ${userName} (chat ID: ${chatId})`);

    const timestampFile = moment().format('YYYYMMDD_HHmmss');
    const backupPath = path.join(__dirname, `backup_${timestampFile}.zip`);

    try {
      const totalBytes = await createBackup(backupPath);
      await sendBackup(chatId, backupPath);

      bot.sendMessage(chatId, `Backup created successfully! Total bytes: ${totalBytes}`);
      console.log(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Backup created successfully. Total bytes: ${totalBytes}`);
    } catch (error) {
      bot.sendMessage(chatId, `Error creating backup: ${error.message}`);
      console.error(`[${moment().format('YYYY-MM-DD HH:mm:ss')}] Error creating backup: ${error.message}`);
    }
  } else if (callbackQuery.data === 'check_disk_usage') {
    bot.sendMessage(chatId, 'Checking disk usage, please wait...');
    console.log(`[${timestamp}] Disk usage check started by ${userName} (chat ID: ${chatId})`);

    await checkDiskUsage(chatId);
  } else if (callbackQuery.data === 'play_guess_the_number') {
    startGame(chatId);
  }
});

// Menangani pesan yang dikirim oleh pengguna
bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const text = msg.text;

  // Memeriksa apakah pesan adalah tebakan dalam game
  if (gameData[chatId]) {
    const guess = parseInt(text, 10);
    if (!isNaN(guess)) {
      handleGuess(chatId, guess);
    } else {
      bot.sendMessage(chatId, 'Please enter a valid number.');
    }
  }
});

console.log('Bot is running...');