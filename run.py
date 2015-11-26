from potato import app

kwargs = {
  'port': 8080,
  'debug': True,
}

app.run('0.0.0.0', **kwargs)