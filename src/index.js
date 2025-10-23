// Minimal Discord bot entry. If DISCORD_TOKEN is not set, this prints instructions.
const token = process.env.DISCORD_TOKEN
if (!token) {
  console.log('DISCORD_TOKEN not set. This repository includes a command handler and test harness.')
  console.log('To run the bot you will need to:')
  console.log('  1) npm install discord.js')
  console.log('  2) export DISCORD_TOKEN=your_token_here')
  console.log('  3) node src/index.js')
  process.exit(0)
}

// Lazy-require discord.js so running tests doesn't need the dependency.
let { Client, Intents } = {}
try {
  ({ Client, Intents } = require('discord.js'))
} catch (err) {
  console.error('discord.js is not installed. Run `npm install discord.js` to enable the bot runtime.')
  process.exit(1)
}

const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] })

const { createCommandHandler } = require('./handler/commandHandler')
const handler = createCommandHandler()

client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}`)
})

client.on('messageCreate', async (message) => {
  if (message.author.bot) return
  if (!message.content.startsWith('!')) return
  const [cmdName, ...args] = message.content.slice(1).trim().split(/\s+/)
  try {
    await handler.handle(cmdName.toLowerCase(), args, {
      reply: (text) => message.reply(text),
      now: () => Date.now(),
      message
    })
  } catch (err) {
    console.error('command error', err)
    message.reply('Something went wrong running that command.')
  }
})

client.login(token)
