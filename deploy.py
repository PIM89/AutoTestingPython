from sshcheckers import ssh_checkout, upload_files


def deploy():
    res = []
    upload_files("0.0.0.0", "user", "1", "/tests/p7zip-full_16.02+transitional.1_all.deb",
                 "/home/user/p7zip-full_16.02+transitional.1_all.deb")
    res.append(ssh_checkout("0.0.0.0", "user", "1",
                            "echo '1' | sudo -S dpkg -i /home/user/p7zip-full_16.02+transitional.1_all.deb",
                            "Setting up p7zip-full"))
    res.append(ssh_checkout("0.0.0.0", "user", "1", "echo '1' | sudo -S dpkg -s p7zip-full",
                            "Status: install ok installed"))
    return all(res)


if deploy():
    print("Деплой успешен")
else:
    print("Ошибка деплоя")