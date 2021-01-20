from subprocess import *

def encrypt_openssl(text, key):
    o = check_output(['echo', text, '|', 'openssl', 'enc', '-aes-128-ecb', '-nosalt', '-K', key , '|', 'xxd', '-p'])
    return o

def en_o(text, key):
    cmd = "echo \"" + text + "\" | openssl enc -aes-128-ecb -nosalt -K " + key + " | xxd -p"
    ps = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT)
    output = ps.communicate()[0]
    print(output)

def en_o2(text, key):
    echo = Popen(['echo', text], stdout=PIPE)
    openssl = Popen(['openssl', 'enc', '-aes-128-ecb', '-nosalt', '-K', key], stdin = echo.stdout, stdout = PIPE)
    xxd = Popen(['xxd', '-p'], stdin = openssl.stdout, stdout = PIPE)
    return xxd.communicate()[0].decode().replace('\n', '')
