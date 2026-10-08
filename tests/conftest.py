import os
import tempfile

# use a throwaway sqlite db for tests, never the real mysql one
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
