# 1. Create virtualenv
# 2. pip3 install pycryptodome

# python3 remmina-decrypt.py $HOME/.config/remmina/remmina.pref ~/.local/share/remmina/THE_NAME_YOU_SAW_IN_REMMINA.remmina

import base64,sys
from Crypto.Cipher import DES3;
pc=open(sys.argv[1]).read();
pci=pc.index('secret=');
secret=pc[pci:pc.index('\n',pci)].split('=',1)[1];cc=open(sys.argv[2]).read();
cci=cc.index('password');
password=cc[cci:cc.index('\n',cci)].split('=',1)[1];
secret,password=base64.b64decode(secret),base64.b64decode(password);
print(DES3.new(secret[:24], DES3.MODE_CBC, secret[24:]).decrypt(password))
