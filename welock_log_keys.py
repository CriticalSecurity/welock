import frida, sys
 
ss = """

function toPrintableString(byteArray) {
  return Array.from(byteArray, function(byte) {
    var charcode = parseInt(('0' + (byte & 0xFF).toString(16)).slice(-2), 16);
    if (charcode < 32 || charcode > 127) {
        return ".";
    } else {
        return String.fromCharCode(charcode); 
    }
  }).join('')
}

function toHexString(byteArray) {
  return Array.from(byteArray, function(byte) {
    return ('0' + (byte & 0xFF).toString(16)).slice(-2);
  }).join('')
}

Java.perform(function() {
    Java.use('javax.crypto.spec.SecretKeySpec').$init.overload('[B', 'java.lang.String').implementation = function(key, algorithm) {
        console.log("SecretKeySpec('" + toHexString(key) + ",'" + algorithm + "') | " + toPrintableString(key));
        return this.$init(key, algorithm);
    };

});

"""

device = frida.get_usb_device()
pid = device.spawn(["cn.sixpower.wlock"])
session = device.attach(pid)
script = session.create_script(ss)
script.load()
device.resume(pid)
sys.stdin.read()
