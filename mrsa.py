import rsa

(pubkey, privkey) = rsa.newkeys(512)

print pubkey

message = "hello"

c = rsa.encrypt(message, pubkey)

m = rsa.decrypt(c, privkey)

print m