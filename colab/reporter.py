import datetime
import functools
import json
import os
import socket
import traceback
import urllib.request
import threading
import time

class Reporter(object):
  def __init__(self, pingme_host):
    self._host = pingme_host
    self._endpoint = f'http://{self._host}/pingme'
    self._queue = []
  
  def _send(self, messages):
    try:
      data = json.dumps(messages).encode('utf8')
      
      req = urllib.request.Request(self._endpoint)
      req.add_header('Host', self._host)
      req.add_header('Accept', '*/*')
      req.add_header('User-Agent', 'curl/7.54.0')
      req.add_header('Connection', 'close')
      req.add_header('Content-Type', 'application/json')
      req.add_header('Content-Length', str(len(data)))
      req.data = data
      
      urllib.request.urlopen(req, timeout=15)
      
      return True
    except socket.timeout as exc:
      print(traceback.format_exc())
      return False
    except urllib.error.URLError as exc:
      print(traceback.format_exc())
      return False
  
  def send(self, message):
    self._queue.append(str(message))
    while True:
      print('trying to send', self._queue)
      if self._send(self._queue):
        del self._queue[:]
        return
      else:
        time.sleep(1)
  
  def __call__(self, func):
    @functools.wraps(func)
    def wrapper_sender(*args, **kwargs):
      base_info = []

      hostname = socket.gethostname()
      base_info.append(self.pair('Machine hostname', hostname))
      
      fqdn = socket.getfqdn()
      if fqdn != hostname:
        base_info.append(self.pair('Machine FQDN', fqdn))
      
      try:
        ip = socket.gethostbyname(hostname)
      except socket.gaierror:
        pass
      else:
        base_info.append(self.pair('Machine IP', ip))
        
      func_name = func.__name__
      base_info.append(self.pair('Main call', func_name))

      start_time = datetime.datetime.now()
      base_info.append(self.pair('Starting date', self.format_date(start_time)))

      # Handling distributed training edge case.
      # In PyTorch, the launch of `torch.distributed.launch` sets up a RANK environment variable for each process.
      # This can be used to detect the master process.
      # See https://github.com/pytorch/pytorch/blob/master/torch/distributed/launch.py#L211
      # Except for errors, only the master process will send notifications.
      if 'RANK' in os.environ:
        rank = os.environ['RANK']
        master_process = int(rank) == 0
        host_name += f' - RANK: {rank}'
      else:
        master_process = True

      if master_process:
        self.send('\n'.join([
          self.title('____________________________'),
          self.title('Your training has started 🎬'),
          *base_info,
        ]))

      try:
        result = func(*args, **kwargs)
      except Exception as exc:
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        
        self.send('\n'.join([
          self.title('____________________________'),
          self.title('Your training has crashed ☠️'),
          *base_info,
          self.pair('Crash date', self.format_date(end_time)),
          self.pair('Crashed training duration', elapsed_time),
          self.subtitle("Here's the error:"),
          self.codeblock(exc),
          self.subtitle('Traceback:'),
          self.codeblock(traceback.format_exc()),
        ]))
        
        raise exc
      else:
        if master_process:
          end_time = datetime.datetime.now()
          elapsed_time = end_time - start_time

          try:
            value_repr = repr(value)
          except:
            value_repr = "ERROR - Couldn't repr the returned value."

          self.send('\n'.join([
            self.title('____________________________'),
            self.title('Your training is complete 🎉'),
            *base_info,
            self.pair('End date', self.format_date(end_time)),
            self.pair('Training duration', elapsed_time),
            self.pair('Main call returned value', value_repr),
          ]))

          text = '\n'.join(contents)
          self.send(text)

        return value

    return wrapper_sender

  def title(self, t):
    return f'<b>{t}</b>\n'
  
  def subtitle(self, t):
    return f'<b>{t}</b>'
  
  def pair(self, k, v):
    return f'<i>{k}:</i> <code>{self.encode(v)}</code>'
  
  def codeblock(self, t):
    return f'<pre>{self.encode(t)}\n</pre>\n'
  
  def format_date(self, d):
    return d.strftime("%Y-%m-%d %H:%M:%S")
  
  def encode(self, t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
