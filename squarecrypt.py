# -*- coding: utf-8 -*-

square = '　▘▝▖▗▀▌▚▞▐▄▛▜▙▟█'

def crypt(origin):
    global square
    crypted = ''
    enc = origin.encode("utf-8")
    for b in enc:
        nums = hex(b)
        for i in str(nums)[2:]:
            # print(i)
            crypted += square[int(i,16)]
    return crypted

def decrypt(enc):
    global square
    charbase = "\\x{}"
    evalbase = "b\"{}\".decode()"
    il = []
    for c in range(0,len(enc),2):
        c1 = hex(square.find(enc[c]))[2:]
        c2 = hex(square.find(enc[c+1]))[2:]
        il.append(c1+c2)
    tmp = ""
    for i in il:
        tmp += charbase.format(i)
    return eval(evalbase.format(tmp))

if __name__ == '__main__':
    t1 = crypt('Nekomaid Preta')
    print(t1)
    print(decrypt(t1))
    t2 = crypt('한국어 테스트')
    print(t2)
    print(decrypt(t2))