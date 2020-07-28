# -*- coding: utf-8 -*-


def atomic(f):
    def wrapper(*args, **kwargs):
        start_transaction()
        result = f(*args, **kwargs)
        end_transaction()
        return result

    return wrapper


def start_transaction():
    print("BEGIN TRANSACTION;")


def end_transaction():
    print("COMMIT TRANSACTION;")


def cancel_transaction():
    print("ROLLBACK TRANSACTION;")
