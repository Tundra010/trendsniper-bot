const fs = require('fs')
const path = require('path')

function createCommandHandler() {
  const commands = new Map()
  // load commands from src/commands
  const commandsPath = path.join(__dirname, '..', 'commands')
  if (fs.existsSync(commandsPath)) {
    for (const file of fs.readdirSync(commandsPath)) {
      if (!file.endsWith('.js')) continue
      const cmd = require(path.join(commandsPath, file))
      if (cmd && cmd.name) commands.set(cmd.name, cmd)
    }
  }

  return {
    async handle(name, args, context) {
      const cmd = commands.get(name)
      if (!cmd) return context.reply(`Unknown command: ${name}`)
      return cmd.execute({ args, ...context })
    },
    list() {
      return Array.from(commands.keys())
    }
  }
}

module.exports = { createCommandHandler }
