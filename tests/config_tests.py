from __future__ import print_function
from nose.tools import *
from uberdoc.config import Config

class TestConfig:

	TEST_CONF_FILE = "tests/uberdoc_tests.cfg"
	TEST_CONF_FILE_USER = "tests/uberdoc_tests_user.cfg"

	def test_basicsetup(self):
		c = Config(self.TEST_CONF_FILE)
		assert_equals(c["in_dir"], "in")
		assert_equals(c["input_ext"], ".md")

	def test_defaults(self):
		c = Config(self.TEST_CONF_FILE,
			{"d1": "default1", "d2": "default2", "in_dir": "other_in_dir"})
		assert_equals(c["in_dir"], "in")
		assert_equals(c["d1"], "default1")
		assert_equals(c["d2"], "default2")

	def test_setting_additional_properties(self):
		c = Config(self.TEST_CONF_FILE)
		c["new_option"] = "new_option_value"
		assert_equals(c["new_option"], "new_option_value")

	def test_user_properties(self):
		c = Config(self.TEST_CONF_FILE)
		assert_equals(len(c.user_items()), 0)

		c_user = Config(self.TEST_CONF_FILE_USER)
		assert_equals(len(c_user.user_items()), 2)
