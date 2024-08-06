# 加密通信机



##### 版本号：1.3.0



## 关于实现：

#### 最底层：依赖于basic_function



basic_function模块定义了一些函数，

**包括但不限于下面两个函数**：

```py
def bytes_to_integers(bytes_sequence, block_size)
作用是，把比特序列按block_size分组，每一组作为一个大整数。


def integers_to_bytes(integers, mode='ignore', block_size=510)
作用是： 把一个或多个大整数，拼接成一个大的字节序列。
```

这是通信时的基本，加密算法依赖于数字，明文是一大堆字节，按指定分组长度，把一堆字节连接成一个大数字。再对这些大数字施展加解密的数学变换。





#### 中层：cry

在cry模块中，已经把basic_function的内容全部导入



##### cry模块中的 RSACipher 类

它实现了：用RSA加密通信

本程序的RSACipher默认均采用： **2048bits密钥   510字节分组长度**

**不建议**更改分组长度



###### 属性简要介绍：

```python
self.plaintext = None   类型应为bytes或bytearray
self.ciphertext = None  类型应为list tuple 型 ,其中的内容应该全为int


这三个是RSA加密的参数，都应该是整数
self.e = public_key
self.d = private_key
self.mod = modulus
```



###### 方法简要介绍：

```Python
class RSACipher(Cipher):
    def __init__(self, public_key=None, private_key=None, modulus=None):

    def generate_keys(self):

    def set_plaintext(self, plaintext):

    def set_ciphertext(self, ciphertext):
        
    def encrypt(self, block_size):
	
    def decrypt(self, block_size):
    
    def file_encrypt(self, source_name, destination_name):

    def file_decrypt(self, source_name):
   
    def __str__(self):
```

`generate_keys`： 用于产生密钥对，返回 `tuple` 类型的  (公钥, 私钥, 模数)。



`set_plaintext` / `set_ciphertext` 用于更改实例的 `plaintext / ciphertext` 属性，虽然可以直接赋值，但是为了不破坏封装原则，建议使用这种办法更改属性



`encrypt` ：将`plaintext`属性加密，记录在`ciphertext`属性，无返回值



`decrypt` ：将`ciphertext`属性解密，记录在`plaintext`属性，无返回值



 `file_encrypt`：

​	在这里，程序以二进制方式打开一个文件（文件名当然由用户指定），将文件的内容全部读出，文件名 和 文件内容连起来, 中间用10个特殊的字节做文件名的结束标识。记录在`plaintext`属性中。

​	设置分隔符变量`separator` = 这10个特殊的字节，**笔者选择的是罕见出现的字节序列，用户可以自行更改**

​	**也就是说**，`plaintext`实际上是 `文件名的utf-8编码` +`separator` + `二进制文件内容`

​	然后调用`encrypt`。密文会记录在`ciphertext`属性中。

​	最后，程序会使用`struct`（标准库）的 `pack` 把 `ciphertext` 中存放的若干个大整数写入目标文件：

​		目标文件中的数据结构：若干个块。每一块分两个部分：

​		`表示大整数长度的字节` + `表示大整数的字节`



`file_decrypt`:

​	程序首先以上述方法读取密文文件。把读到的所有大整数记录在`ciphertext`属性里

​	然后。调用`decrypt`, 此时明文字节序列已经被记录在 `plaintext`属性里

​	**上面已经说明：`plaintext`实际上是 `文件名的utf-8编码` +`separator` + `二进制文件内容`**

​	所以，程序再以这十个特殊字节做分隔，把`plaintext`分成这两个部分。解码出文件名，并将二进制文件内容写入这个文件名对应的文件。





#### 上层实现：加密通信机.py

pass

​	





