from tkinter import *
from PIL import Image, ImageTk
import dependencies.crypto as crypto
import configparser
import subprocess

def copy_to_clipboard(text):
    # 使用echo命令和clip命令复制文本到剪贴板
    # text.strip()方法用于去掉字符串开头和结尾的空白字符，防止因为文本中的空白字符导致命令格式错误。
    # | 是管道符号，用于将前一个命令的输出作为下一个命令的输入。
    # text应为str类型,但如果传入列表或元组，也可以运行
    if type(text) == list or type(text) == tuple:
        text = " ".join(map(str, text))

    cmd = 'echo ' + text.strip() + '| clip'
    subprocess.run(cmd, shell=True)

# 定义加密、解密等函数
def encrypt():
    # 需要做一个新的界面，用于加解密。
    def update_status(flag):
        if flag == 0:
            status_label.config(text="密文未加密完成\n请勿点击下方复制到剪切板按钮", font=("华文新魏", 40))
        elif flag == 1:
            status_label.config(text="密文已经加密完成\n可以点击下方按钮复制到剪切板", font=("华文新魏", 40))

    def submit():
        # 用于提交文本框中的明文，并算出密文
        plaintext = entry.get("1.0", "end-1c")
        entry.delete("1.0", "end")
        plaintext = plaintext.encode('utf-8')
        send_cryptor.set_plaintext(plaintext)
        send_cryptor.encrypt()

        update_status(flag=1)# 更新标签内容。

    send_cryptor, receive_cryptor = generate_cryptor()

    encrypt_win = Tk()
    encrypt_win.title("纯文本加密")  # 设置窗口标题
    encrypt_win.geometry("900x700")  # 设置窗口大小

    # 创建一个较大的文本框
    entry = Text(encrypt_win, width=100, height=20, borderwidth=5)
    entry.pack()

    # 创建一个显示文本的标签,并时刻更新标签文本。
    status_label = Label(encrypt_win, text="")
    status_label.pack()
    update_status(flag=0)

    # 创建加密按钮
    button_submit = Button(encrypt_win, text='开始加密', command=submit)
    button_submit.pack(pady=20)

    # 创建复制到剪切板按钮
    button_copy = Button(encrypt_win, text='复制密文到剪切板', command=lambda: copy_to_clipboard(send_cryptor.ciphertext))
    button_copy.pack(pady=20)

    # 运行主循环
    encrypt_win.mainloop()

def decrypt():
    def update_status(flag):
        if flag == 0:
            status_label.config(text="明文未解密完成\n请勿点击下方复制到剪切板按钮", font=("华文新魏", 20))
        elif flag == 1:
            status_label.config(text=receive_cryptor.plaintext.decode('utf-8'), font=("华文新魏", 20))

    def submit():
        # 获取文本框里面的密文，然后解密。
        ciphertext = entry.get("1.0", "end-1c")# -1c是为了去掉末尾的换行符
        entry.delete("1.0", "end")
        # 这时获取到的ciphertext是以空格分隔的字符串，如“1 2 3”，需将其处理为[1, 2, 3]的列表
        ciphertext = ciphertext.split(' ')
        ciphertext = [int(number) for number in ciphertext]
        receive_cryptor.set_ciphertext(ciphertext)
        receive_cryptor.decrypt(mode='ignore')

        update_status(flag=1)  # 更新标签内容。

    send_cryptor, receive_cryptor = generate_cryptor()

    win = Tk()
    win.title("纯文本解密")  # 设置窗口标题
    win.geometry("900x700")  # 设置窗口大小

    # 创建一个较大的文本框
    entry = Text(win, width=100, height=20, borderwidth=5)
    entry.pack()

    # 创建一个显示文本的标签,并时刻在需要时更新标签文本。
    status_label = Label(win, text="")
    status_label.pack()
    update_status(flag=0)

    # 创建解密按钮
    button_submit = Button(win, text='开始解密', command=submit)
    button_submit.pack(pady=20)

    # 创建复制到剪切板按钮
    button_copy = Button(win, text='复制明文到剪切板',
                         command=lambda: copy_to_clipboard(receive_cryptor.plaintext.decode('utf-8')))
    button_copy.pack(pady=20)

    # 运行主循环
    win.mainloop()

def file_encrypt():
    def update_status(flag):
        if flag == 0:
            status_label.config(text="密文文件未加密完成", font=("华文新魏", 20))
        elif flag == 1:
            status_label.config(text="密文文件已经加密完成\n请查看相应文件", font=("华文新魏", 20))

    def submit():
        # 用于提交两个文本框中的文件名。
        source_name = source_entry.get("1.0", "end-1c")
        destination_name = destination_entry.get("1.0", "end-1c")
        source_entry.delete("1.0", "end")
        destination_entry.delete("1.0", "end")

        send_cryptor.file_encrypt(source_name, destination_name)

        update_status(flag=1)# 更新标签内容。

    send_cryptor, receive_cryptor = generate_cryptor()

    win = Tk()
    win.title("文件加密")  # 设置窗口标题
    win.geometry("900x700")  # 设置窗口大小

    #先设置两个输入提示标签
    label_1 = Label(win, text='请在此输入要加密的文件名')
    label_2 = Label(win, text='请在此输入希望生成的目标文件名')
    label_1.place(x=100, y=50)
    label_2.place(x=600, y=50)

    #设置两个Text文本框
    source_entry = Text(win, width=40, height=10, borderwidth=5)
    destination_entry = Text(win, width=40, height=10, borderwidth=5)
    source_entry.place(x=50, y=100)
    destination_entry.place(x=550, y=100)

    #设置一个状态标签，用于显示是否已经完成加密操作
    status_label = Label(win, text='')
    status_label.place(x=300, y=300)
    update_status(0)

    #设置提交button
    button_submit = Button(win, text='开始加密,加密时窗口会锁死', command=submit)
    button_submit.place(x=350, y=450)

    win.mainloop()

def file_decrypt():
    def update_status(flag, text=''):
        if flag == 0:
            status_label.config(text="明文文件未解密完成", font=("华文新魏", 20))
        elif flag == 1:
            status_label.config(text=f"明文文件已经解密完成\n请查看相应文件\n密文已经保存为{text}", font=("华文新魏", 20))

    def submit():
        # 用于提交文本框中的文件名。
        source_name = source_entry.get("1.0", "end-1c")
        source_entry.delete("1.0", "end")

        destination_name = receive_cryptor.file_decrypt(source_name)
        update_status(flag=1, text=destination_name)# 更新标签内容。

    send_cryptor, receive_cryptor = generate_cryptor()

    win = Tk()
    win.title("文件解密")  # 设置窗口标题
    win.geometry("900x700")  # 设置窗口大小

    #先设置输入提示标签
    label_1 = Label(win, text='请在此输入要解密的文件名')
    label_1.place(x=350, y=50)

    #设置Text文本框
    source_entry = Text(win, width=40, height=10, borderwidth=5)
    source_entry.place(x=280, y=100)

    #设置一个状态标签，用于显示是否已经完成操作
    status_label = Label(win, text='')
    status_label.place(x=300, y=300)
    update_status(0)

    #设置提交button
    button_submit = Button(win, text='开始解密,解密时窗口会锁死\n解密用时可能较长', command=submit)
    button_submit.place(x=350, y=450)

    win.mainloop()


def generate_cryptor():
    # 根据algorithm，产生出send_cryptor和receive_cryptor
    def RSA_set_config():
        # 读取配置文件,destination是信宿名
        # 创建ConfigParser对象,         读取配置文件
        global destination

        config = configparser.ConfigParser()
        config.read('配置文件.ini')

        my_private_key = int(config['myself']['private_key'])
        my_public_key = int(config['myself']['public_key'])
        my_mod = int(config['myself']['mod'])

        try:
            receiver_public_key = int(config[destination][destination + '_public_key'])
            receiver_mod = int(config[destination][destination + '_mod'])
        except KeyError:
            print('不存在此用户, 配置文件读取失败哦')
            exit(1)

        # 返回值是(send_cryptor, receiver_cryptor)
        send_cryptor = crypto.RSACipher(public_key=receiver_public_key, modulus=receiver_mod)  # 加密消息时所用的密码机
        receive_cryptor = crypto.RSACipher(public_key=my_public_key, private_key=my_private_key,
                                          modulus=my_mod)  # 解密消息所用
        return send_cryptor, receive_cryptor

    def ElGamal_set_config():
        pass

    def ECC_set_config():
        pass

    if algorithm == 'RSA':
        return RSA_set_config()
    elif algorithm == 'ElGamal':
        return ElGamal_set_config()
    elif algorithm == 'ECC':
        return ECC_set_config()

# 打开主菜单窗口
def open_menu_window():
    menu = Tk()
    menu.title('加密通信机  by  QlanCheng')
    menu.geometry('900x700')  # 这里的乘号不是 * ，而是小写英文字母 x

    def generate_destination_label():
        # 创建用于显示当前信宿的标签
        text = StringVar()
        text.set('当前信宿    ' + destination)

        win_destination = Label(menu, textvariable=text, font=("华文新魏", 16))
        win_destination.place(relx=0.1, rely=0.05, relwidth=0.3, relheight=0.10)

    def generate_algorithm_label():
        # 创建用于显示当前加密算法的标签
        text = StringVar()
        text.set('当前加密算法    ' + algorithm)
        win_alg = Label(menu, textvariable=text, font=("华文新魏", 16))
        win_alg.place(relx=0.6, rely=0.05, relwidth=0.3, relheight=0.10)


    # 纯文本加密按钮
    image_encrypt = Image.open("picture/芙芙1.png")
    background_encrypt = ImageTk.PhotoImage(image_encrypt)
    button_encrypt = Button(menu, image=background_encrypt, text="纯文本加密", command=encrypt, width=20, height=2, font=("华文新魏", 40), compound="center", fg='black')
    button_encrypt.place(relx=0.1, rely=0.3, relwidth=0.3, relheight=0.15)

    # 纯文本解密按钮
    image_decrypt = Image.open("picture/芙芙2.jpg")
    background_decrypt = ImageTk.PhotoImage(image_decrypt)
    button_decrypt = Button(menu, image=background_decrypt, text="纯文本解密", command=decrypt, width=20, height=2, font=("华文新魏", 40), compound="center", fg='black')
    button_decrypt.place(relx=0.1, rely=0.7, relwidth=0.3, relheight=0.15)

    # 文件加密按钮
    image_file_encrypt = Image.open("picture/芙芙3.jpg")
    background_file_encrypt = ImageTk.PhotoImage(image_file_encrypt)
    button_file_encrypt = Button(menu, image=background_file_encrypt, text="文件加密", command=file_encrypt, width=20, height=2, font=("华文新魏", 40), compound="center", fg='white')
    button_file_encrypt.place(relx=0.6, rely=0.3, relwidth=0.3, relheight=0.15)

    # 文件解密按钮
    image_file_decrypt = Image.open("picture/芙芙4.jpg")
    background_file_decrypt = ImageTk.PhotoImage(image_file_decrypt)
    button_file_decrypt = Button(menu, image=background_file_decrypt, text="文件解密", command=file_decrypt, width=20, height=2, font=("华文新魏", 40), compound="center", fg='white')
    button_file_decrypt.place(relx=0.6, rely=0.7, relwidth=0.3, relheight=0.15)


    generate_algorithm_label()
    generate_destination_label()
    menu.mainloop()

# 初始窗口，用于用户输入信宿、密钥体制。同时用户可以产生密钥对。
def start_program():
    global algorithm
    global destination

    # 创建窗口
    start_window = Tk()
    start_window.title('加密通信机  by  QlanCheng')
    start_window.geometry('500x250')


    def algorithm_select(window):
        # 创建单选框，选择密钥体制
        choice = IntVar()  # 算法选项
        choice.set(-1)  # 设置一个非法的选项，使得初始时刻，所有选项都不被选中

        def mysel():
            # 点击Radiobutton后执行的操作
            global algorithm
            dic = {0: 'RSA', 1: 'ElGamal', 2: 'ECC'}
            algorithm = dic.get(choice.get())
            #print(algorithm)

        rd1 = Radiobutton(window, text="RSA", variable=choice, value=0, command=mysel)
        rd2 = Radiobutton(window, text="ElGamal", variable=choice, value=1, command=mysel)
        rd3 = Radiobutton(window, text="ECC", variable=choice, value=2, command=mysel)

        # 使用place方法设置单选按钮的位置
        rd1.place(x=50, y=70)
        rd2.place(x=50, y=100)
        rd3.place(x=50, y=130)


    def entry_blank():
        # 创建一个简单的输入框和按钮,用于输入信宿
        def on_submit():
            # 创建提交按钮
            # 点击提交后，会销毁掉start_window  并获取到destination值
            # algorithm值在按选项按钮的时候立即获取,无需依赖此按钮
            global destination
            destination = entry.get()
            start_window.destroy()
            open_menu_window()

        Label(start_window, text="请输入信宿:\n初次使用请点击下方按钮产生密钥对").pack(pady=20)
        entry = Entry(start_window)
        entry.pack(pady=10)
        Button(start_window, text="提交", command=on_submit).pack(pady=20)  # 创建提交按钮


    def generate_keys():
        # 首先需要创建出一个新窗口，摧毁start_window,然后在新窗口中选择algorithm，并产生密钥对。
        def RSA_keys():
            cryptor = crypto.RSACipher()
            print(str(cryptor))
            return str(cryptor)

        def ElGamal_keys():
            pass

        def ECC_keys():
            pass

        def start():
            # 根据algorithm值，决定将要执行的密钥生成函数
            keys = 'default'
            if algorithm == 'RSA':
                keys = RSA_keys()
            elif algorithm == 'ElGamal':
                keys = ElGamal_keys()
            elif algorithm == 'ECC':
                keys = ECC_keys()

            file = open('keys.txt', 'w')
            file.write(str(keys))

            # 以关闭window窗口
            window.destroy()
            # 以关闭python程序
            exit(0)

        start_window.destroy()

        window = Tk()
        window.title('加密通信机  by  QlanCheng')
        window.geometry('500x250')

        algorithm_select(window=window) # 选择密钥体制

        # 显示一些信息
        Label(window, text="按下方按钮开始生成\n请稍等，产生密钥对需要时间。不会超过几分钟\n完成后程序会自动关闭\n密钥将会保存在同目录下的keys.txt, 请注意查看\n生成时窗口会卡死").place(x=150, y=0)


        # 定义一个start Button，点击后开始产生密钥对
        start_button = Button(window, text="已完成选择", command=start)
        start_button.place(x=230, y=150)

        window.mainloop()




    algorithm_select(window=start_window) # 创建算法选择栏
    entry_blank()# 创建输入框, 包括：1. 输入提示标签 2. 输入框 3.提交按钮
    Button(start_window, text="产生密钥对", command=generate_keys).pack(pady=5)  # 产生密钥对的按钮, 按下之后会引发generate_keys函数执行
    start_window.mainloop()


if __name__ == '__main__':

    # 调用初始窗口函数启动程序
    algorithm = 'default'
    destination = 'default'
    start_program()
