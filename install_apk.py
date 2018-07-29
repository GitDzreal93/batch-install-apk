# __author__ = 'Dzreal'
# __date__ = '2018-07-28 0:57'
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor as Pool
from concurrent.futures import as_completed


def get_apk():
    '''
    获取apk包
    :return: apk
    '''
    apk_dir = os.path.join(os.getcwd(), 'apks')
    if not os.path.exists(apk_dir):
        os.mkdir(apk_dir)
    apk_list = os.listdir(apk_dir)
    if len(apk_list) == 0:
        print('没有可以安装的apk，请在apk目录下放置一个待安装的apk文件')
        exit()
    else:
        apk = os.path.join(apk_dir, apk_list[0])
        return apk


def get_devices():
    '''
    获取设备列表
    :return: devices_list
    '''
    device_dir = os.path.join(os.getcwd(), 'devices')
    if not os.path.exists(device_dir):
        os.mkdir(device_dir)
    devices_list = []
    t = time.strftime('%Y%m%d_%H%M', time.localtime())
    cmd_devices = 'adb devices'
    p = subprocess.Popen(cmd_devices, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    line = p.stdout.read()
    with open(os.path.join(device_dir, 'devices_info_{}.txt'.format(t)), 'wb+') as f:
        f.write(line)
    with open(os.path.join(device_dir, 'devices_info_{}.txt'.format(t)), 'r') as f:
        lines = f.readlines()[1:-1]
        for line in lines:
            (device, status) = line.split()
            if status == 'device':
                devices_list.append(device)
    return devices_list


def check_pkg_exists(device):
    '''
    判断设备上是不是已经安装了apk
    :param device:
    :return: BOOL
    '''
    is_exists = False
    pkg = 'com.ss.android.article.news'
    cmd_check_pkg = 'adb -s {} shell pm list packages -3 | findstr {}'.format(device, pkg)
    p = subprocess.Popen(cmd_check_pkg, stdout=subprocess.PIPE, shell=True)
    out = p.communicate(input=subprocess.PIPE)[0]
    if out:
        print('手机上已经安装了今日头条app')
        is_exists = True
    else:
        print('手机上没有安装今日头条app')
    return is_exists


def install_apk(device, apk):
    '''
    安装apk
    :param device:
    :param apk:
    :return:
    '''
    # 判断今日头条是否已经安装，若没有安装的话，提醒用户是否覆盖安装
    is_exists = check_pkg_exists(device)
    # 提醒用户是否覆盖安装由于是阻塞操作，实力有限，暂时还没有想通怎么去处理，现在默认是重新覆盖安装
    # if is_exists:
    #     flag = input("手机上已经安装了今日头条app，是否需要重新安装？[y|n] \n")
    #     if flag == 'y':
    #         cmd_install_r = 'adb -s {} install -r {}'.format(device, apk)
    #         p = subprocess.Popen(cmd_install_r, stdout=subprocess.PIPE, shell=True)
    #         try:
    #             # out = p.communicate(input=subprocess.PIPE)[0]
    #             out = p.communicate()[0]
    #             print(out)
    #             status = p.poll()
    #             if status == 0:
    #                 print("安装成功\n")
    #             else:
    #                 print("安装失败 \n")
    #         except Exception as e:
    #             print(e)
    #             p.kill()
    #     elif flag == 'n':
    #         print('退出该次安装')
    #         pass

    # 若首次安装则走下面的逻辑
    cmd_install = 'adb -s {} install {}'.format(device, apk)
    # 若之前用户已经安装过了，默认重新覆盖安装
    if is_exists:
        cmd_install = 'adb -s {} install -r {}'.format(device, apk)
        print("默认重新安装今日头条")
    p = subprocess.Popen(cmd_install, stdout=subprocess.PIPE, shell=True)
    try:
        out = p.communicate()[0]
        # print(out)
        # out = p.communicate(input=subprocess.PIPE)[0]
        status = p.poll()
        if status == 0:
            print("安装成功\n")
        else:
            print("安装失败 \n")
    except Exception as e:
        print(e)
        p.kill()


if __name__ == '__main__':
    apk = get_apk()
    devices = get_devices()
    # 多线程并行装包
    with Pool(max_workers=5) as executor:
        future_tasks = [executor.submit(install_apk, device, apk) for device in devices]
        for f in as_completed(future_tasks):
            try:
                ret = f.done()
                if ret:
                    f_ret = f.result()
                    # print(f_ret)
            except Exception as e:
                f.cancel()
                # print(str(e))
