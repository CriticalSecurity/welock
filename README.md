# WE.LOCK: Unlocking Smart Locks with Web Vulnerabilities

### Intro
[WE.LOCK](https://welockglobal.com/) is a smart home access solution provider that manufactures and sells smart locks. WE.LOCK smart locks can be unlocked using a fingerprint, access codes, RFID tags, a smartphone app via Bluetooth (BLE) or the physical key supplied with a lock. In this article we are focusing on a smartphone app for Android, a mobile API, and the security of both.

A new version (v3.1.1) of the [WeLock](https://play.google.com/store/apps/details?id=cn.sixpower.wlock) app for Android was released on May 24, 2021. The changelog notes that the UI was updated, but what is not mentioned is that the mobile app was bound to a new mobile API. There is a reason for this as the old API, which is still supported, was probably designed without security in mind and therefore suffers from multiple critical security vulnerabilities. These vulnerabilities can be easily exploited for gaining access to arbitrary user accounts and unlocking all the smart locks that are linked to a target account.

Next chapters describe one of the identified vulnerabilities perfectly illustrating how bad the security of the old mobile API is. The vendor has not responded to our vulnerability notification attempts, but we suspect that the vendor might be aware of the security issues and therefore has started migrating to the new (current) mobile API. Until the old and insecure API is shut down, commercial or residential properties secured with WE.LOCK smart locks are at risk.

### Mobile Application Reversing
The version 2.5.8.0427 of WeLock app for Android (released on April 27, 2021) and earlier versions connect to the API endpoint welock.we-lock.com.cn. The app is protected with the Jiagu packer, the classes.dex file is encrypted, but the packer does not prevent dynamic instrumentation. Furthermore, the communication between the app and the mobile API endpoint takes place over an unencrypted channel (HTTP). To compensate this, parameter strings and responses are encrypted using the Triple-DES encryption algorithm. The encryption key is hardcoded inside the mobile application and can be extracted (without dealing with the Jiagu packer) either from a captured heap dump of the running app or using a dynamic instrumentation framework, such as [Frida](https://frida.re/). 

A simple python [script](welock_log_keys.py), which utilizes Frida, was written. Its primary purpose is to hook the Java class *SecretKeySpec* and log secret keys, including the Triple-DES key:

![welock_log_keys.py](https://user-images.githubusercontent.com/79406206/120490975-27db9480-c3b9-11eb-87af-960f18d672a3.png)

### Web Application Vulnerabilities
The mobile API provides a couple of handlers, which can be used to call different actions. The request parameter *parmsStr* holds an encrypted and Base64 encoded parameter string. For example, the *userBleList2* action expects the parameter string to be in the format “Mobile=11111111111”. In this case, the digits represent a mobile phone number that is associated with a user account. Neither the parameter string nor the corresponding HTTP request contains a session identifier or an access token, which would indicate that it is an authenticated API call. This suggests that all an attacker needs to make this API call is the mobile phone number of the owner of the target smart lock.

The following HTTP POST request illustrates the *userBleList2* action call. The WeLock app adds custom HTTP headers, such as *Usersession* and *sessionId*, but no actual values are being transmitted:
```
POST //Handler/Ashx_userBle.ashx?Action=userBleList2 HTTP/1.1
Appkey: 
Udid: 
Os: android
Osversion: 
Appversion: 
Sourceid: 
Ver: 
Userid: 
Usersession: 
Unique: 
sessionId: 
Content-Length: 41
Content-Type: application/x-www-form-urlencoded
Host: welock.we-lock.com.cn
Connection: close
User-Agent: Mozilla/5.0 (Linux; U; Android 10; en-us; Pixel Build/QP1A.190711.020) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1
Accept-Encoding: gzip, deflate

parmsStr=EGAga/fKnPxprPR6FdM9SgLVddLkLSDW
```
The *userBleList2* action returns the configuration details of all the smart locks that are linked to a specific account, which is indicated by a mobile phone number. The [welock_crypto_tool.py](welock_crypto_tool.py) tool implements the API call to the *userBleList2* action and takes care of the encryption of a parameter string and the decryption of a response (after inserting the extracted Triple-DES key). The tool can be used to retrieve configuration details, when only a mobile phone number of an existing user account is known:

![welock_crypto_tool.py](https://user-images.githubusercontent.com/79406206/120492356-4a21e200-c3ba-11eb-8c2f-35bb5524a80a.png)

The configuration details include an encrypted (with the same Triple-DES key) communication password. The WeLock app uses this password to unlock a smart lock via a BLE connection. The [welock_crypto_tool.py](welock_crypto_tool.py) tool can also be used to decrypt the encrypted BLE communication password:

![communication_password](https://user-images.githubusercontent.com/79406206/120492487-6887dd80-c3ba-11eb-9425-953f3e577340.png)

At this point an attacker, who is in a close proximity to a target smart lock, would be able to initiate a BLE connection and unlock the target smart lock using the decrypted communication password. 

As we can see, the old API allows us to retrieve passwords and other confidential information while only knowing the phone number of a victim.

### Disclosure timeline:
- 2021-01-07 – Contacting WE.LOCK support about security vulnerabilities, no response.
- 2021-03-04 – Contacting WE.LOCK support about security vulnerabilities, no response.
- 2021-05-06 – Contacting WE.LOCK support about security vulnerabilities, no response.
- 2021-06-02 – Article released.
