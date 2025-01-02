from server import Manager, create_app

app = create_app()

if __name__ == "__main__":
    try:
        Manager.load()
        Manager.connect()
    except Exception as err:
        print(err)
