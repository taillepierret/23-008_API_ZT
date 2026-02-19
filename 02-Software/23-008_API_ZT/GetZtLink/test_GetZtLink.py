from GetZtLink import getZtLink


if __name__ == "__main__":
    success,link = getZtLink()
    print(success,link)
    assert success == True
    assert link == "https://zerotier.com/download/"