export TEST_CRYPTBOXFS=true
export TEST_CRYPTBOXFS_PASSWORD=password123

python cryptboxfs.py _foobar/ foobar/ cryptbox_test_config.json cryptbox_test_keys.json $@
