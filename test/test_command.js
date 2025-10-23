const { createCommandHandler } = require('../src/handler/commandHandler')

async function run() {
  const handler = createCommandHandler()
  const outputs = []
  const context = {
    reply: (text) => outputs.push(text),
    now: () => Date.now()
  }

  await handler.handle('ping', [], context)

  if (outputs.length === 0) {
    console.error('Test failed: no reply from ping command')
    process.exit(2)
  }

  console.log('Test outputs:')
  console.log(outputs.join('\n'))
  console.log('OK')
}

run().catch(err => {
  console.error('Test error', err)
  process.exit(1)
})
