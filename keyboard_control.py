import sys,select,termios,tty

def getKey(key_timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


if __name__=='__main__':
	i = 0
	settings = termios.tcgetattr(sys.stdin)
	while(i<10):
		print('safasfsdf')
		key = getKey(None)
		print(key)
		i+=1
	exit
