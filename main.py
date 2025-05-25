import callmonitoringsystem
import getaccesstoken


def main():
    # access_token = getaccesstoken.get_access_token()
    smtp = callmonitoringsystem.create_smtp_connection()
    callmonitoringsystem.get_call_history(access_token='1000.cbb5f44f730a5e47cf51f8014500516a.d98af814c8a32c33570f5a4908c58f4f',smtp=smtp)
    smtp.quit()


if __name__ == '__main__':
    main()