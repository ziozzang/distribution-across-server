#!//usr/bin/python
# -*- coding: UTF-8 -*-
##############################################
#
# Script by Jioh L. Jung (ziozzang@gmail.com)
#
import pexpect
import os

# 작업할 서버 목록
servers = ["1.2.3.4"]
# 패스워드가 혼재된 경우에 목록으로 명시.
#ex) passwords = ["pass1", "pass2"]
passwords = []
# 각 서버에 로그인할 계정
server_id = "sys"


# SCP로 복사해올 서버
hostid = "sys"
hostpw = ""
hostip = "1.1.1.1"


# 비밀번호가 설정되지 않은 경우 중단.
if len(hostpw) < 1 or len(passwords) <1:
  exit(1)


# 한개 이상의 패스워드를 확인함.
def check_pw(s):
  global passwords
  pw = ""
  for i in range(len(passwords)+1):
    j = s.expect(["\~\$", "password"], timeout=10)
    if j == 1:
      try:
        pw = passwords[i]
      except:
        return None
      s.sendline(pw)
    else:
      return pw


# 인증키 copy & sudoers 언락.
def cp2srv(ip):
  global hostpw, hostid, server_id
  print "=== %s : Starting... ===" % ip
  s = pexpect.spawn("ssh -o StrictHostKeyChecking=no %s@%s" % (server_id,ip))
  pw = check_pw(s)
  if pw is None:
    print " > %s password is failed." % ip
    s.close()
    print " === Ending ==="
    return False

  print " > .ssh directory...",
  s.sendline("[ -d .ssh ] || mkdir .ssh")
  s.expect("\~\$", timeout=10)
  s.sendline("chmod 700 .ssh")
  s.expect("\~\$", timeout=10)
  print "done"

  print " > scp is ...",
  s.sendline("rcp  -o StrictHostKeyChecking=no %s@%s:~/.ssh/authorized_keys ." % (hostid,hostip))
  j = s.expect(["\~\$", "password"], timeout=10)
  if j == 1:
    s.sendline(hostpw)
  else:
    pass
  s.sendline("[ -f .ssh/authorized_keys ] && echo \"\n\" >> .ssh/authorized_keys")
  s.expect("\~\$", timeout=10)
  s.sendline("[ -f .ssh/authorized_keys ] || touch .ssh/authorized_keys")
  s.expect("\~\$", timeout=10)
  s.sendline("cat authorized_keys >> .ssh/authorized_keys")
  s.expect("\~\$", timeout=10)
  s.sendline("rm authorized_keys")
  s.expect("\~\$", timeout=10)
  print "done"

  print " > Acquire root ...",
  s.sendline("sudo su")
  j = s.expect(["\#", "password"], timeout=10)
  if j == 1:
    s.sendline(pw)
    s.expect("\#", timeout=10)
  else:
    pass
  s.sendline("cd ~")
  s.expect("\~\#", timeout=10)
  print "done"

  print " > Add to user sudoers...",
  s.sendline("echo \"%s ALL=(ALL) NOPASSWD: ALL\" >  /etc/sudoers.d/%s" %(
    server_id, server_id))
  s.expect("\~\#", timeout=10)
  s.sendline("chmod 0440 /etc/sudoers.d/%s"% (server_id))
  s.expect("\~\#", timeout=10)
  print "done"

  s.close()
  print "=== Ending ==="
  return True

for i in servers:
  cp2srv(i)
