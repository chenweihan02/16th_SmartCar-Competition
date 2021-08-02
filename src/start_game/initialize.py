#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import getpass
import time
import hashlib
import platform
import tarfile
from interactive import show, get_bool_ans, get_str_ans, save

model_path = '~/gazebo_test_ws/src/gazebo_pkg/urdf'
workspace_path = 'source ~/gazebo_test_ws/devel/setup.bash'

def install_pkg():
    '''
    apt 安装依赖
        ros-melodic-teleop-twist-keyboard
        ros-melodic-rqt-graph
    '''
    print("\nros-melodic-teleop-twist-keyboard\nros-melodic-rqt-graph\n")
    if get_bool_ans('需要上述ROS包，是否自动安装（如已安装可跳过）？'):
        show('正在尝试安装依赖...')
        os.system('sudo apt update')
        os.system('sudo apt install ros-melodic-teleop-twist-keyboard ros-melodic-rqt-graph -y')
        if not get_bool_ans('是否安装成功？'):
            show('请手动安装后继续')
            exit(0)
        else:
            show('安装成功')
    else:
        show('已跳过安装依赖')

def md5sum(path):
    '''
        计算文件 MD5 摘要
    '''
    with open(path, "rb") as f:
        file_hash = hashlib.md5(f.read())
    return file_hash.hexdigest()

def md5sum_dir(source_dir, md5_result=None):
    '''
        计算文件夹下所有文件 MD5

        这里后期其实可以优化一下，对外只暴露一个 md5sum() 接口，然后函数内部检查传入的path
        指向文件夹还是文件（可以用 os.path.isfile 方法），如果是文件夹则调用 md5sum_dir()，
        否则调用 md5sum_file()，最后返回参数为 list 类型，但我懒得改了
    '''
    if md5_result is None:
        md5_result = []                                              # python 传递可变对象为引用。故不可直接写为 def func(..., md5_result=[])

    source_dir = os.path.expanduser(source_dir)
    for root, dirs, files in os.walk(source_dir):
        for name in files:
            fullname = os.path.join(root, name)
            md5_result.append(md5sum(fullname))
            show(md5_result[-1], name)
            save(md5_result[-1], name)                               # 输出并保存
    return md5_result

""" def dir_to_tar(*source_dirs):                                    # 失败的尝试————把 tar 解压再打包回 tar 会改变 hash
    '''
    将 src_path 中指定的文件夹打包为 .tar 文件
    由于打包的目的是进行校验（文件夹无法直接进行 MD5 校验）
    这里就干脆直接放到 /tmp 目录下，不必指定打包后的存放路径
    '''
    with tarfile.open('/tmp/final.tar',"w") as tar:
        for source_dir in source_dirs:
            source_dir = os.path.expanduser(source_dir)
            tar.add(source_dir, arcname=os.path.basename(source_dir))

def extract_from_tar(src_path, dest_path):
    '''
    将 src_path 中指定的 .tar 文件提取到 dest_path 中
    '''
    with tarfile.open(src_path, "r:") as tar:
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, dest_path)
    return os.path.join(dest_path, os.path.basename(src_path)[:-4]) """

def search_str(path, words):
    '''
        在指定文件中搜索字符串，若存在字串则返回 True
        未检查路径是否合法，请调用时自行确保路径的有效性
    '''    
    result = os.popen("cat %s | grep '%s'" %(path, words)).read().strip('\n')
    if len(result) == 0:
        return False
    else:
        return True

def check_system():
    '''
    检查执行本脚本的操作系统
    '''
    if platform.system() != 'Linux':
        show('必须使用 带有 gnome 桌面的 Unix 系统 执行本脚本！')
        exit(0)

def check_user():
    '''
    检查执行本脚本的用户
    '''
    if os.getuid() == 0:
        show('不要使用root用户执行本脚本！')
        exit(0)
    else:
        show('Username:', getpass.getuser())
    
def build_pkg():
    '''
    提取文件
    这里没有使用 os.path 库，而是直接拼接文件路径，因此一定注意文件夹路径
    '''

    show('正在创建资源包...')
    
    # os.system('mkdir -p ~/.gazebo/models')
    # os.system('cp -r resources/ucar_plane/* ~/.gazebo/models')
    os.system('mkdir -p ~/iflytek_gazebo_ws/src')
    os.system("cp -r resources/gazebo_pkg ~/iflytek_gazebo_ws/src && \
        cd ~/iflytek_gazebo_ws && \
        catkin_make -DCATKIN_WHITELIST_PACKAGES='gazebo_pkg'")
    
    while get_bool_ans('上述编译信息是否出现错误？'):
        show('请尝试手动解决错误后继续！')
        exit(0)
    
    show('已成功创建工作空间 ~/iflytek_gazebo_ws')

def config_py2_encoding():
    '''
    通过修改 sitecustomize.py 改变默认编码
    '''
    show('正在尝试修改 python2 默认编码为 utf-8...')

    lib_path = '/usr/lib/python2.7/sitecustomize.py'
    if not search_str(lib_path, 'setdefaultencoding'):
        os.system(""" echo "\nimport sys\nreload(sys)\nsys.setdefaultencoding('utf-8')" | sudo tee -a %s > /dev/null 2>&1""" %lib_path)
        show('修改完成')
    else:
        show("已存在对应配置，无需修改")
    os.system('python2 %s' % lib_path)

def config_env():
    '''
    修改环境变量，若环境变量中已存在对应配置则不修改
    '''
    show('正在修改环境变量...')

    env_path = '~/.bashrc'
    words = workspace_path
    if not search_str(env_path, words):
        os.system("echo '%s' >> ~/.bashrc" %words)
        show('环境变量已正确配置')
    else:
        show('环境变量已正确配置，无需修改')

def init():
    '''
    初始化，包括环境检查、MD5 校验等
    '''
    logo = """

    ██╗███████╗██╗     ██╗   ██╗████████╗███████╗██╗  ██╗
    ██║██╔════╝██║     ╚██╗ ██╔╝╚══██╔══╝██╔════╝██║ ██╔╝
    ██║█████╗  ██║      ╚████╔╝    ██║   █████╗  █████╔╝ 
    ██║██╔══╝  ██║       ╚██╔╝     ██║   ██╔══╝  ██╔═██╗ 
    ██║██║     ███████╗   ██║      ██║   ███████╗██║  ██╗
    ╚═╝╚═╝     ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
    """
    print(logo)
    show(time.strftime("%a %b %d %Y, Timezone: %Z", time.localtime()))
    save(time.strftime("%a %b %d %Y %H:%M:%S, Timezone: %Z", time.localtime()))
    show('比赛记录脚本 Ver0.1')
    show('Platform:', platform.platform())
    
    check_system()
    check_user()

    while not get_bool_ans('是否已开启录屏？'):
        show('请按照规则开启录屏！')

    md5_result = md5sum_dir(model_path)                             # 计算原始文件 MD5 摘要

#    build_pkg()
    config_env()
    # config_py2_encoding()
    # install_pkg()

    return md5_result

def uninit():
    '''
    收尾工作，包括 MD5 校验等
    '''
    show(time.strftime("%a %b %d %Y, Timezone: %Z", time.localtime()))

    # md5_result = md5sum_dir('~/.gazebo/models')
    # md5_result = md5sum_dir('~/iflytek_gazebo_ws/src/gazebo_pkg', md5_result)
    md5_result = md5sum_dir(model_path)

    
    return md5_result


