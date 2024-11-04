from checkers import *
from sshcheckers import *

import yaml

with open('config.yaml') as f:
    data = yaml.safe_load(f)


def save_log(start_time, name):
    with open(name, 'w') as f:
        f.write(getout("journalctl --since '{}'".format(start_time)))


class TestPositive:
    def test_connect_and_install(self, start_time):
        res = []
        upload_files(data["host"], data["username"], data["password"], data["local_path"], data["remote_path"])
        res.append(ssh_checkout(data["host"], data["username"], data["password"],
                                "echo '{}' | sudo -S dpkg -i {}".format(data["password"], data["remote_path"]),
                                "Setting up p7zip-full"))
        res.append(ssh_checkout(data["host"], data["username"], data["password"],
                                "echo '{}' | sudo -S dpkg -s {}".format(data["password"], data["pkg_name"]),
                                "Status: install ok installed"))
        save_log(start_time, data["file_name"])
        assert all(res)

    def test_step1(self, get_stat, connect_to_remote, make_folders, clear_folders, make_files):
        # test1
        res1 = checkout("cd {}; 7z a {}/arx".format(data["folder_in"], data["folder_out"]), "Everything is Ok")
        res2 = checkout("ls {}".format(data["folder_out"]), "arx.7z")
        assert res1 and res2, "test1 FAIL"

    def test_step2(self, get_stat, connect_to_remote, clear_folders, make_files):
        # test2
        res = []
        res.append(checkout("cd {}; 7z a {}/arx".format(data["folder_in"], data["folder_out"]), "Everything is Ok"))
        res.append(
            checkout("cd {}; 7z e arx.7z -o{} -y".format(data["folder_out"], data["folder_ext"]), "Everything is Ok"))
        for item in make_files:
            res.append(checkout("ls {}".format(data["folder_ext"]), item))
        assert all(res)

    def test_step3(self, get_stat, connect_to_remote):
        # test3
        assert checkout("cd {}; 7z t arx.7z".format(data["folder_out"]), "Everything is Ok"), "test3 FAIL"

    def test_step4(self, get_stat, connect_to_remote):
        # test4
        assert checkout("cd {}; 7z u arx2.7z".format(data["folder_in"]), "Everything is Ok"), "test4 FAIL"

    def test_step5(self, get_stat, connect_to_remote, clear_folders, make_files):
        # test5
        res = [checkout("cd {}; 7z a {}/arx".format(data["folder_in"], data["folder_out"]), "Everything is Ok")]
        for i in make_files:
            res.append(checkout("cd {}; 7z l arx.7z".format(data["folder_out"], data["folder_ext"]), i))
        assert all(res), "test5 FAIL"

    def test_step6(self, get_stat, connect_to_remote, clear_folders, make_files, make_subfolder):
        # test6
        res = [checkout("cd {}; 7z a {}/arx".format(data["folder_in"], data["folder_out"]), "Everything is Ok"),
               checkout("cd {}; 7z x arx.7z -o{} -y".format(data["folder_out"], data["folder_ext2"]),
                        "Everything is Ok")]
        for i in make_files:
            res.append(checkout("ls {}".format(data["folder_ext2"]), i))
        res.append(checkout("ls {}".format(data["folder_ext2"]), make_subfolder[0]))
        res.append(checkout("ls {}/{}".format(data["folder_ext2"], make_subfolder[0]), make_subfolder[1]))
        assert all(res), "test6 FAIL"

    def test_step7(self, get_stat, connect_to_remote):
        # test7
        assert checkout("cd {}; 7z d arx.7z".format(data["folder_out"]), "Everything is Ok"), "test7 FAIL"

    def test_step8(self, get_stat, connect_to_remote, clear_folders, make_files):
        # test8
        res = []
        for i in make_files:
            res.append(checkout("cd {}; 7z h {}".format(data["folder_in"], i), "Everything is Ok"))
            hash_crc32 = getout("cd {}; crc32 {}".format(data["folder_in"], i)).upper()
            res.append(checkout("cd {}; 7z h {}".format(data["folder_in"], i), hash_crc32))
        assert all(res), "test8 FAIL"


class TestNegative:
    def test_negative_step1(self, get_stat, connect_to_remote, make_folders):
        assert checkout_negative("cd {}; 7z e arx2.7z -o{}".format(data["folder_out"], data["folder_ext"]),
                                 "ERROR: "), "test_negative_step1 FAIL"

    def test_negative_step2(self, get_stat, connect_to_remote, make_files, make_bad_arx):
        assert checkout_negative("cd {}; 7z t arxbad.7z".format(data["folder_out"]),
                                 "ERROR: "), "test_negative_step2 FAIL"


class TestDeleteApp:
    def test_delete(self):
        res = [ssh_checkout(data["host"], data["username"], data["password"],
                            "echo '{}' | sudo -S dpkg -r {}".format(data["password"], data["pkg_name"]),
                            "Removing p7zip-full"),
               ssh_checkout(data["host"], data["username"], data["password"],
                            "echo '{}' | sudo -S dpkg -s {}".format(data["password"], data["pkg_name"]),
                            "Status: deinstall ok config-files"),
               ssh_checkout(data["host"], data["username"], data["password"],
                            "rm -rf /home/{}/*".format(data["username"]), "")]
        assert all(res), "Application uninstall test failed"

# echo 1 | sudo -S dpkg -r p7zip-full
# echo 1 | sudo -S dpkg -i /home/pim/PycharmProjects/seminar4_paramiko/tests/p7zip-full_16.02+transitional.1_all.deb
# echo 1 | sudo -S dpkg -s p7zip-full

# userdel user; useradd user -m; usermod -aG sudo user; passwd user

# ls | grep -v t | xargs rm -rfv
