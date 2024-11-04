import paramiko
import pytest

from checkers import checkout, getout
import random, string
import yaml
from datetime import datetime

with open('config.yaml') as f:
    data = yaml.safe_load(f)


@pytest.fixture()
def make_folders():
    return checkout("mkdir {} {} {} {}".format(data["folder_in"], data["folder_out"], data["folder_ext"],
                                               data["folder_ext2"]), "")


@pytest.fixture()
def clear_folders():
    return checkout("rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"], data["folder_out"], data["folder_ext"],
                                                        data["folder_ext2"]), "")


@pytest.fixture()
def make_files():
    list_of_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if checkout("cd {}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_in"], filename,
                                                                                           data["bs"]), ""):
            list_of_files.append(filename)
    return list_of_files


@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if not checkout("cd {}; mkdir {}".format(data["folder_in"], subfoldername), ""):
        return None, None
    if not checkout(
            "cd {}/{}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_in"], subfoldername,
                                                                                      testfilename, data["bs"]), ""):
        return subfoldername, None
    else:
        return subfoldername, testfilename


@pytest.fixture(autouse=True)
def print_time():
    print("Start: {}".format(datetime.now().strftime("%H:%M:%S.%f")))
    yield
    print("Finish: {}".format(datetime.now().strftime("%H:%M:%S.%f")))


@pytest.fixture()
def make_bad_arx():
    checkout("cd {}; 7z a {}/arxbad".format(data["folder_in"], data["folder_out"]), "Everything is Ok")
    checkout("truncate -s 1 {}/arxbad.7z".format(data["folder_out"]), "Everything is Ok")
    yield "arxbad"
    checkout("rm -rf /home/user/*", "")


@pytest.fixture()
def get_stat():
    time_start = datetime.now()
    yield
    exec_time = datetime.now() - time_start
    stat_proc = getout("cat /proc/loadavg")
    file_stat = open("stat.txt", "a+")
    file_stat.write(
        "Время:{}, количество файлов:{}, размер файла:{}, статистика загрузки процессора:{}".format(
            exec_time, data["count"], data["bs"], stat_proc))
    file_stat.close()


@pytest.fixture()
def start_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@pytest.fixture()
def connect_to_remote():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=data["host"], username=data["username"], password=data["password"], port=data["port"])
    yield
    client.close()
