import sys, json, requests
from Crypto.Cipher import DES3
from base64 import b64decode, b64encode

key = b"insert_the_extracted_3DES_key_here"
url = "http://welock.we-lock.com.cn/Handler/Ashx_userBle.ashx?Action=userBleList2"

def des3_encrypt(key, data):
    encryptor = DES3.new(key, DES3.MODE_ECB)
    pad_len = 8 - len(data) % 8 
    padding = chr(pad_len) * pad_len
    data += padding
    return encryptor.encrypt(data)

def des3_decrypt(key, data):
    encryptor = DES3.new(key, DES3.MODE_ECB)
    result = encryptor.decrypt(data)
    pad_len = result[-1]
    result = result[:-pad_len]
    return result

def print_help(name):
    print("Usage: %s command argument" % name)
    print("\nCommands:\n",
    "get_config <mobile_number>",
    "decrypt <base64_string>",
    "encrypt <plain_string>",
    sep="\n"
    )
    
if __name__=='__main__':
    if len(sys.argv) != 3:
        print_help(sys.argv[0])
        sys.exit(1)
    
    if sys.argv[1] == "get_config":
        paramstr = b64encode(des3_encrypt(key, "Mobile={0}".format(sys.argv[2])))
        post_data = {"parmsStr": paramstr}
        response = requests.post(url = url, data = post_data)
        decrypted_data = des3_decrypt(key, b64decode(json.loads(response.content.decode('utf-8'))["data"]))
        print(json.dumps(json.loads(decrypted_data.decode()), indent=4))
    elif sys.argv[1] == "decrypt":
        print(des3_decrypt(key, b64decode(sys.argv[2])).decode())
    elif sys.argv[1] == "encrypt":
        print(b64encode(des3_encrypt(key, sys.argv[2])).decode())
    else:
        print_help(sys.argv[0])
        sys.exit(1)

