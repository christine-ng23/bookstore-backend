## common/config.py

SECRET = 'supersecretjwtkey'  # private key used to sign/verify JWT using in Auth Server + Resource Server
CLIENT_ID = 'client123'  # registered with Authenticate Server
CLIENT_SECRET = 'secret456' # registered with Authenticate Server
TOKEN_EXPIRE_MINUTES = 60000
AUTH_SERVER = "http://localhost:5000"
FRONTEND_SERVER = "http://localhost:3000"
