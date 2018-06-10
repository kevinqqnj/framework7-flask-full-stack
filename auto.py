# encoding: utf-8
# auto build (phonegap+Framework7+vue+Flask), then git push to heroku
# http://psutil.readthedocs.io/
# python auto.py -h: means push to heroku

import os, sys, time, re
import psutil
from subprocess import PIPE

GIT_REMOTE = 'heroku'
INDEX_HTML = 'app/templates/index.html'
NODE_DIR = "C:/Program Files/nodejs/"
if not os.path.exists(NODE_DIR):
  NODE_DIR = "C:/Program Files (x86)/nodejs/"
  NODE = NODE_DIR + "node.exe"
  PHONEGAP = NODE_DIR + "node_modules/phonegap/bin/phonegap.js"
  if not os.path.exists(PHONEGAP):
    PHONEGAP = 'C:/Users/{}/AppData/Roaming/npm/'.format(os.environ.get('username')) + 'node_modules/phonegap/bin/phonegap.js'
# Linux
if not os.path.exists(NODE_DIR):
  PHONEGAP = 'phonegap'


def find_procs_by_name(name):
  "Return a list of processes matching 'name'."
  ls = []
  for proc in psutil.process_iter():
      try:
          pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
          if pinfo['name'].lower().find(name)>-1:
              print(pinfo)
              ls.append(pinfo['pid'])
      except psutil.NoSuchProcess:
          print(proc.as_dict)
  return ls

################################################################
#                      主程序开始                              #
################################################################
if __name__ == '__main__':
  usg = """
  -? 显示本信息
  -h git push remote "heroku", not "origin"
  -m git commit "msg"，用双引号表示, "msg" must be last argv
  """
  if '-?' in sys.argv:
    print(usg)
    exit()
  if not '-h' in sys.argv:
    GIT_REMOTE = 'origin'
  GIT_MSG = '"auto"'
  if '-m' in sys.argv:
    GIT_MSG = '"{}"'.format(sys.argv[-1])
    # for aa in sys.argv:

  with psutil.Popen(['git', 'status'], stdout=PIPE) as proc:
    rsp = (proc.stdout.read().decode('utf8'))
    is_changed = "no changes added to commit"
    is_clear = "nothing to commit, working directory clean"
    if rsp.find(is_changed):
      print(rsp)
    else:
      input(is_clear)
      exit()

  print('closing current node.exe...')
  for p in find_procs_by_name('node'):
    psutil.Process(p).terminate()
  print('======== run phonegap build...')

  if PHONEGAP=='phonegap':
    p_cmd = [PHONEGAP, 'build', '--release']
  else:
    p_cmd = [NODE, PHONEGAP, 'build', '--release']
  with psutil.Popen(p_cmd, stdout=PIPE) as proc:
  # with psutil.Popen(["ipconfig"], stdout=PIPE) as proc:
    print(proc.stdout.read().decode('utf8'))   # 中文系统用 .decode('gbk'), 英文系统：'ascii'
  # os.remove('app/static/main.css')
  # os.remove('app/static/main.js')

  print('======== copy main.js, styles.css to app/static')
  # 删除旧的js/css
  olds = os.listdir('app/static')
  for f in olds:
    if re.search('main[\d]{3,}.', f): os.remove('app/static/'+f)
  stamp = str(time.time()).split('.')[0]
  # 移动+改名
  os.rename('www/main.js', 'app/static/main{}.js'.format(stamp))
  os.rename('www/styles.css', 'app/static/main{}.css'.format(stamp))

  print('======== update main.js&main.css in index.html')
  with open(INDEX_HTML, 'r') as f:
    html = f.read()
  html = re.sub('main[\d]{3,}.js', 'main{}.js'.format(stamp), html)
  html = re.sub('main[\d]{3,}.css', 'main{}.css'.format(stamp), html)
  html = re.sub('value="[\d]{3,}"', 'value="{stamp}"'.format(stamp=stamp), html)	# 转义{} -> {{}}
  with open(INDEX_HTML, 'w') as f:
    f.write(html)

  print('======== git push to Heroku...')
  with psutil.Popen(['git', 'add', '.'], stdout=PIPE) as proc:
    print(proc.stdout.read().decode('ascii'))
  with psutil.Popen(['git', 'commit', '-m', GIT_MSG], stdout=PIPE) as proc:
    print(proc.stdout.read().decode('ascii'))
  # print(proc.communicate())
  with psutil.Popen(['git', 'push', GIT_REMOTE, 'master'], stdout=PIPE) as proc:
    print(proc.stdout.read().decode('ascii'))

  # print('Done!')
  input('Done!')
