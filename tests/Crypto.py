# -*- coding: utf-8 -*-
"""
    Test case for efesto's cryptographic module.
    
"""
import sys
sys.path.insert(0, "")
import pytest
import random
import string


from efesto.Base import config
from efesto.Crypto import generate_hash, compare_hash


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def test_hash_generation():
    """
    Tests the hash generation function
    """
    h = generate_hash('mystring')
    shards = h.split('$')
    assert len(shards) == 4
    assert shards[0] == 'PBKDF2-256'
    assert shards[1] == config.parser.get('security', 'iterations')
    assert len(shards[2]) == config.parser.getint('security', 'salt_length')*2
    assert len(shards[3]) == config.parser.getint('security', 'key_length')*2


def test_hash_generation_randomness():
    """
    Tests whether generate_hash can return different hashes for the same string
    """
    some_random_string = random_string(6)
    first_key = generate_hash(some_random_string)
    second_key = generate_hash(some_random_string)
    assert second_key != first_key


def test_compare_hash():
    """
    Tests the hash comparison function.
    """
    first_key = generate_hash('mypassword')
    assert compare_hash('mypassword', first_key)


def test_compare_hash_failure():
    """
    Tests whether the comparison fails for different strings.
    """
    first_key = generate_hash('mypassword')
    assert compare_hash('notmypassword', first_key) == False
