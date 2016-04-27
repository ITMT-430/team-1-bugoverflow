from test import app as application
from mydb import rebuilddb

if __name__ == "__main__":
    rebuilddb()
    app.run()
