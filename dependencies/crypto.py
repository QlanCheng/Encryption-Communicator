from .basic_func import *
import struct

class BothPlainAndCipherError(Exception):
    def __init__(self, message="Both plaintext and ciphertext were provided. Please provide only one."):
        self.message = message
        super().__init__(self.message)


class Cipher:
    def encrypt(self):
        raise NotImplementedError

    def decrypt(self):
        raise NotImplementedError
    
    
class AffineCipher(Cipher):
    def __init__(self, multiplier, addend, mod, plaintext=bytearray(), ciphertext=bytearray(), mode='use'):
        if mode not in ['use', 'attack']:
            raise ValueError('Mode can be "use" or "attack"')
        if plaintext:
            if (not isinstance(plaintext, bytes)) and (not isinstance(plaintext, bytearray)):
                raise TypeError("plaintexts must be encoded before encryption")
        if ciphertext:
            if (not isinstance(ciphertext, bytes)) and (not isinstance(ciphertext, bytearray)):
                raise TypeError("ciphertexts must be encoded before decryption")

        if mode == 'use': #使用模式
            if plaintext and ciphertext:
                raise BothPlainAndCipherError
            if not all([isinstance(attr, int) for attr in [multiplier, addend, mod]]):
                raise TypeError("Parameters(multiplier, addend, mod) must be integer")
            self.multiplier = multiplier
            self.addend = addend
            self.mod = mod
            self.plaintext = bytearray(plaintext)
            self.ciphertext = ciphertext

        else:#破译密钥模式，选择密文攻击，使用时输入明文和与之对应的密文
            self.plaintext = plaintext
            self.ciphertext = ciphertext
            self.mod = mod
            self.attack()

        gcd, s, t = EEA(self.mod, self.multiplier)
        if gcd != 1:
            raise ValueError(f"gcd({multiplier}, {mod}) is not 1")
        else:
            self.inverse = t % mod

    def append_plaintext(self, plaintext):
        if (not isinstance(plaintext, bytes)) and (not isinstance(plaintext, bytearray)):
            raise TypeError("Plaintexts must be encoded before encryption")
        self.plaintext = self.plaintext + bytearray(plaintext)

        for byte in plaintext:
            cipher = mod_mult(multiplier=self.multiplier, base=byte, addend=self.addend, mod=self.mod)
            self.ciphertext.append(cipher)

    def append_ciphertext(self, ciphertext):
        if (not isinstance(ciphertext, bytes)) and (not isinstance(ciphertext, bytearray)):
            raise TypeError("ciphertexts must be encoded before encryption")
        self.ciphertext = self.ciphertext + bytearray(ciphertext)

        for byte in ciphertext:
            plain = mod_mult(multiplier=self.inverse, base=byte-self.addend, addend=0, mod=self.mod)
            self.plaintext.append(plain)




    def encrypt(self):
        if self.plaintext and self.ciphertext:
            raise BothPlainAndCipherError
        for byte in self.plaintext:
            cipher = mod_mult(multiplier=self.multiplier, base=byte, addend=self.addend, mod=self.mod)
            self.ciphertext.append(cipher)


    def decrypt(self):
        if self.plaintext and self.ciphertext:
            raise BothPlainAndCipherError
        for byte in self.ciphertext:
            plain = mod_mult(multiplier=self.inverse, base=byte-self.addend, addend=0, mod=self.mod)
            self.plaintext.append(plain)


    def clear(self):
        self.plaintext = bytearray()
        self.ciphertext = bytearray()

    def attack(self):
        right = (self.ciphertext[0] - self.ciphertext[1])
        left = (self.plaintext[0] - self.plaintext[1])
        left_inverse = EEA(self.mod, left)[2] % self.mod
        self.multiplier = (left_inverse * right) % self.mod
        self.addend = (self.ciphertext[0] - (self.plaintext[0] * self.multiplier)) % self.mod




    def __str__(self):
        return f"c = {self.multiplier} * m + {self.addend} (mod {self.mod})"


class RSACipher(Cipher):
    def __init__(self, public_key=None, private_key=None, modulus=None):
        self.plaintext = None
        self.ciphertext = None
        args = [public_key, private_key, modulus]


        if not any(args):#用户没有给出任何参数，需要生成密钥
            self.e, self.d, self.mod = self.generate_keys()
        else:#用户给出两个或者三个参数,使用模式，无需产生密钥
            for arg in args:
                if arg and type(arg) != int:
                    raise TypeError('args must be integer')

            self.e = public_key
            self.d = private_key
            self.mod = modulus

    def generate_keys(self):
        min = 2**2042
        max = 2**2048
        while True:
            while True:#选p
                p = random.randint(min, max)
                if is_probable_prime(p, repetitions=20, mode='fermat'):
                    print('P is ready')
                    break
            while True:#选q
                q = random.randint(min, max)
                if is_probable_prime(q, repetitions=20, mode='fermat'):
                    break
            if abs(p-q) >= 2**150:#确保p和q差距很大
                print('P, Q is ready')
                break
        n = p * q
        phi_n = (p - 1) * (q - 1)
        e = 65537        #选取公钥e，默认是常用的65537，可以保证加密速度很快

        #开始选取私钥
        gcd, s, t = EEA(phi_n, e)
        if gcd != 1:
            raise ValueError('gcd != 1')
        #这里t就是私钥，但是要模一下phi_n
        d = t % phi_n
        print('All is successful')

        return e, d, n


    def set_plaintext(self, plaintext):
        if type(plaintext) not in [bytes, bytearray]:
            raise TypeError('Type of ciphertext should be bytes or bytearray ')
        self.plaintext = plaintext


    def set_ciphertext(self, ciphertext):
        #ciphertext的类型应该是装有多段cipher的可迭代对象，或者一个int数字
        #这里仅支持list tuple int 型
        if type(ciphertext) not in [list, tuple]:
            raise TypeError('Type of ciphertext should be list\ tuple\ int ')
        self.ciphertext = ciphertext


    def encrypt(self, block_size=510):
        plaintexts = bytes_to_integers(bytes_sequence=self.plaintext, block_size=block_size)
        # 按指定分组长度，连接成一个个大数字。再对这些大数字施展加解密的数学变换。
        self.ciphertext = [pow(plaintext, self.e, self.mod) for plaintext in plaintexts]


    def decrypt(self, mode='ignore', block_size=510):
        if mode not in ['ignore', 'reserve']:
            raise ValueError('mode必须是ignore或者reserve')

        integers = [pow(cipher, self.d, self.mod) for cipher in self.ciphertext]  # 解密出的一堆明文数字，用列表承装
        # 然后对这些明文数字，使用integers_to_bytes方法，转换成bytearray
        bytes_sequence = integers_to_bytes(integers=integers, mode=mode, block_size=block_size)
        self.plaintext = bytes_sequence


    def file_encrypt(self, filename ,destination_name='cipher'):
        # 文件名会一齐进入加密文件中
        try:
            file = open(filename, mode='rb')
        except FileNotFoundError:
            print('文件不存在，检查路径或文件名')
            exit(1)
        except OSError:
            print('其他未知错误')
            exit(1)

        filename = file.name  # 不带路径了。

        # 文件名 和 文件内容连起来之后一齐加密 , 中间用10个特殊的字节做文件名的结束标识
        separator = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
        bytes_sequence = bytearray(filename.encode('utf-8')) + separator + bytearray(file.read())
        print(bytes_sequence)
        # 把bytes_sequence设置成plaintext属性，然后运用encrypt方法
        self.set_plaintext(bytes_sequence)
        self.encrypt()

        # 打开目标文件并写入数据
        destination_file = open(destination_name, mode='wb')

        for number in self.ciphertext:
            byte_data = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big')
            # 写入字节数组的长度（作为前缀）
            destination_file.write(struct.pack('I', len(byte_data)))
            # 写入字节数组
            destination_file.write(byte_data)

        print('密文文件已经保存为:', destination_name)



    def file_decrypt(self, source_name):
        # 打开密文文件
        try:
            source = open(source_name, mode='rb')
        except FileNotFoundError:
            print('文件不存在，检查路径或文件名')
            exit(1)
        except OSError:
            print('其他未知错误')
            exit(1)

        ciphertext = []  # 密文

        while True:
            # 读取字节数组的长度（前缀）
            length_data = source.read(4)
            if not length_data:
                break  # 到达文件末尾
            length = struct.unpack('I', length_data)[0]
            # 读取字节数组
            byte_data = source.read(length)
            # 将字节数组转换回大整数
            number = int.from_bytes(byte_data, byteorder='big')
            ciphertext.append(number)

        self.set_ciphertext(ciphertext=ciphertext)
        self.decrypt(mode='reserve', block_size=510)

        # separator分隔，前面的一段是文件名，后面的一段是文件内容
        separator = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
        index = self.plaintext.find(separator)# 查找第一个separator出现的位置

        destination_name, content = self.plaintext[:index], self.plaintext[index + len(separator):]
        destination_name = destination_name.decode('utf-8', errors='replace')
        # destination_name解码为字符串，content直接以二进制形式写入。

        destination = open(destination_name, 'wb')
        destination.write(content)

        print('明文文件已经保存为:', destination_name)
        return destination_name

    def __str__(self):
        string = f"""公钥:{self.e}
私钥:{self.d}
模数:{self.mod}"""

        return string



if __name__ == '__main__':
    pass