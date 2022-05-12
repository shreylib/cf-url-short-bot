import os

class Config(object):
	BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
	SHORTENER_DOMAIN = os.environ.get("SHORTENER_DOMAIN", "")
	EXT_TOKEN = os.environ.get("EXT_TOKEN", "")
	ADMIN_IDS = os.environ.get("ADMIN_IDS", "") # ==> Enter Admin Chat IDs here !!
