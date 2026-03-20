import pypowerwall
import os

def get_pw_api():
    host = os.getenv('POWERWALL_HOST', "192.168.91.1")
    gw_pwd = os.getenv('POWERWALL_GW_PWD', "")
    password = os.getenv('POWERWALL_PASSWORD', "")
    email = os.getenv('POWERWALL_EMAIL', "")
    timezone = os.getenv('POWERWALL_TIMEZONE', "Pacific/Auckland")

    return pypowerwall.Powerwall(host, password, email, timezone, gw_pwd=gw_pwd, auto_select=True)

def main():
    pw_api = get_pw_api()

if __name__ == '__main__':
    main()

