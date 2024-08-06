import random
import math

def EEA(r0, r1):#eea算法，把r_i表示成r0和r1的线性组合
    if type(r0) != int or type(r1) != int:
        raise TypeError("arguments must be integer!  参数必须是整数")

    if r1 > r0:
        print("Warning! Normally, The second parameter should be smaller than the first parameter. ")

    s = [1, 0]#r0的系数
    t = [0, 1]#r1的系数
    q = []#商
    r = [r0, r1]#余数
    i = 1
    while True:
        i += 1
        r_i = r[i-2] % r[i-1]
        r.append(r_i)#余数
        q.append(r[i-2] // r[i-1])#商

        s_i = s[i-2] - q[i-2] * s[i-1]
        t_i = t[i-2] - q[i-2] * t[i-1]
        s.append(s_i)
        t.append(t_i)

        if r_i == 0:
            return r[i-1], s[i-1], t[i-1]


def is_probable_prime(n, repetitions=20, mode='fermat'):
    if type(n) != int or type(repetitions) != int:
        raise TypeError("N and Repetitions must be integer!  参数必须是整数")
    if mode not in ['miller_rabin', 'fermat']:
        raise ValueError("Mode must be 'miller_rabin' or 'fermat'")

    # 如果 n 是 2 或 3，返回 True
    if n == 2 or n == 3:
        return True
    # 如果 n 是 1 或者是偶数，返回 False
    if n == 1 or n % 2 == 0:
        return False

    import random
    if mode == 'miller_rabin':
        # 将 n-1 分解为 2^s * d，其中 d 是奇数
        s = 0
        d = n - 1
        while d % 2 == 0:
            d //= 2
            s += 1

        for i in range(repetitions):
            # 随机选择一个基 a
            a = random.randint(2, n - 2)
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for j in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True
    else:
        for i in range(repetitions):
            a = random.randint(2, n - 2)
            # 计算 a^(n-1) % n
            if pow(a, n - 1, n) != 1:
                return False

        return True


def discrete_logarithm(result, base, mod, max_iterations=10):
    if not all(isinstance(arg, int) for arg in [result, base, mod]):
        raise TypeError("All parameters must be integers.  参数必须是整数")

    success_probability = 1 - 0.5**max_iterations

    def create_tableA(base, mod):
        import random
        tableA = dict()
        for counter in range(0, int(mod ** 0.5)):
            a = random.randint(0, mod - 1)
            ga = pow(base, a, mod)
            tableA[ga] = a  # 键是ga,值是a,方便查询
        return tableA  # 用字典是因为字典是底层是用哈希表实现的，查找速度非常快。

    def create_tableB(result, base, mod):
        import random
        tableB = dict()
        for counter in range(0, int(mod ** 0.5)):
            b = random.randint(0, mod - 1)
            ygb = (result * pow(base, b, mod)) % mod
            tableB[ygb] = b
        return tableB

    while max_iterations:
        max_iterations -= 1

        tableA = create_tableA(base, mod)
        tableB = create_tableB(result, base, mod)
        keysA = set(tableA.keys())
        keysB = set(tableB.keys())
        common_results = keysA & keysB
        if common_results:
            common_item = common_results.pop()
            a, b = tableA[common_item], tableB[common_item]
            return (a - b) % (mod - 1)
        else:
            continue

    raise TimeoutError(f"""
    Exceeded maximum iterations ({max_iterations}) without finding a solution.
超过最大循环次数({max_iterations})次.若您确定参数无误.尝试改变max_iterations的值? 或再试一次? 当前成功概率为{success_probability}
""")


def mod_mult(multiplier, base, addend, mod):
    result = 0
    base = base % mod
    while multiplier > 0:
        if (multiplier % 2) == 1:  # 如果 b 是奇数
            result = (result + base) % mod
        base = (base * 2) % mod
        multiplier //= 2

    result = (result + addend) % mod
    return result


def bytes_to_integers(bytes_sequence, block_size):
    #作用是，把比特序列按block_size分组，每一组作为一个大整数。
    #返回一个列表，其中装着这些大整数
    #转换法则是，不足block_size的不补0。
    if type(bytes_sequence) not in [bytes, bytearray]:
        raise TypeError('第一个参数(比特序列)类型必须是bytes或者bytearray')

    integers = []
    for i in range(0, len(bytes_sequence), block_size):
        bytes_block = bytes_sequence[i:i + block_size]
        new_number = int.from_bytes(bytes_block, 'big')
        integers.append(new_number)

    return integers


def integers_to_bytes(integers, mode='ignore', block_size=510):
    #bytes_to_integers函数的逆变换
    #作用是： 把一个或多个大整数，拼接成一个大的字节序列。
    #返回值：bytearray类型

    #问题 1 ：
    #例如十进制的2，它可能由00000010转换而来; 也可能是由00000000 00000010转换而来; 或者若干个全0字节，最低字节是00000010转换而来
    #对待这种情况，有zero参数来控制，zero=ignore时,忽略全0字节。zero=reserve时,按Block_size，保留全0字节
    #问题 2 :
    #有时候block_size无法满足转换需求，例如block_size = 1时; 无法将65536用一个字节表示
    #解决方法: 发生这种错误时，会引发OverflowError， 捕获它，然后令block_size自适应+1，直到加到合适值
    #(一般情况下，需要+1的次数并不会很多)，也就是说，用户输入的block_size与真正需求的block_size绝大情况下都一样。


    bytes_sequence = bytearray(0)    #作为返回值，初始化为空的bytearray对象

    if mode == 'ignore':
        for number in integers:
            # 计算需要多少字节来表示这个十进制数 (每个字节8位)
            num_bits = number.bit_length()
            num_bytes = math.ceil(num_bits / 8)
            while True:
                try:
                    bytes_block = bytearray(number.to_bytes(length=num_bytes, byteorder='big'))
                    #to_bytes方法的返回类型是bytes，强制转换成bytearray
                    break
                except OverflowError:
                    num_bytes += 1
            bytes_sequence = bytes_sequence + bytes_block

    if mode == 'reserve':
        for number in integers:
            while True:
                try:
                    bytes_block = bytearray(number.to_bytes(length=block_size, byteorder='big'))
                    #to_bytes方法的返回类型是bytes，强制转换成bytearray
                    break
                except OverflowError:
                    print('overflow')
                    a = input('请查看提示')
                    exit(1)
            bytes_sequence = bytes_sequence + bytes_block

    return bytes_sequence


if __name__ == '__main__':
    pass