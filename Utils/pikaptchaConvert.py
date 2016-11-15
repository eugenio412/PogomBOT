import sys
import logging
import os

if len(sys.argv) > 1:
    jsonPath = os.path.join(sys.argv[1], "usernames.txt")
else:
    jsonPath = "usernames.txt"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

accs = 0
acc_type = []
acc_user = []
acc_pass = []

try:
    with open(jsonPath, "r") as f:
        for line in f:
            line = line.replace('\r', '').replace('\n', '')
            if line.startswith('The following accounts use the email address:'):
                logger.info('No Account: <%s>' % (line))
            else:
                tmp = line.split(':')
                if len(tmp) > 1:
                    acc_type.append("ptc")
                    acc_user.append(tmp[0])
                    acc_pass.append(tmp[1])
                    accs += 1
                    logger.info('Account: <%s>' % (line))
                else:
                    logger.info('No Account: <%s>' % (line))

        print ("Accounts gesamt: %d" % (accs))

        print ('--- for pokemongo-map config.ini:')
        str = ""
        for w in acc_type:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("auth-service: [%s]" % (str))

        str = ""
        for w in acc_user:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("username: [%s]" % (str))

        str = ""
        for w in acc_pass:
            str = "%s, %s" % (str, w)
        str = str[2:]
        print ("password: [%s]" % (str))


except Exception as e:
    logger.error('%s' % (repr(e)))

