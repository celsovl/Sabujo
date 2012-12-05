import unittest as ut

if __name__ == '__main__':
	suite = ut.defaultTestLoader.discover('.')
	ut.TextTestRunner(verbosity=2).run(suite)
