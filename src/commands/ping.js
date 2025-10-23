module.exports = {
  name: 'ping',
  description: 'Responds with Pong and latency',
  async execute(context) {
    const start = context.now()
    const latency = Date.now() - start
    return context.reply(`Pong! ${latency}ms`)
  }
}
module.exports = {
  name: 'ping',
  description: 'Responds with Pong and latency info',
  async execute(context) {
    // context: { reply: fn, now: fn }
    const start = context.now()
    // simulate minimal processing
    const latency = Date.now() - start
    return context.reply(`Pong! ${latency}ms`)
  }
}
