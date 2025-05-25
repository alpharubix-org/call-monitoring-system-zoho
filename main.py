import callmonitoringsystem
import getaccesstoken


def main():
    access_token = getaccesstoken.get_access_token()
    smtp = callmonitoringsystem.create_smtp_connection()
    callmonitoringsystem.get_call_history(access_token=access_token,smtp=smtp)
    smtp.quit()


if __name__ == '__main__':
    main()