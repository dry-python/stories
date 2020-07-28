# Transaction management

It's possible to handle database transactions in different ways inside stories.

## Single steps

If you need to wrap single story step in a database transaction, don't do that
inside the step itself. Stories you write should not be aware of the database
you use.

Ideally, stories are written with composition in mind. So you'll be able to
decorate injected function in the construction process.

```pycon

>>> from dataclasses import dataclass
>>> from typing import Callable
>>> from stories import story, arguments, Success, Failure

>>> @dataclass
... class Purchase:
...
...     @story
...     @arguments('user_id')
...     def make(I):
...         I.lock_item
...         I.charge_money
...         I.notify_user
...
...     def lock_item(self, ctx):
...         self.lock_item_query()
...         return Success()
...
...     def charge_money(self, ctx):
...         self.charge_money_query()
...         return Success()
...
...     def notify_user(self, ctx):
...         ok = self.send_notification(ctx.user_id)
...         if ok:
...             return Success()
...         else:
...             return Failure()
...
...     lock_item_query: Callable
...     charge_money_query: Callable
...     send_notification: Callable

```

You don't need to wrap with transaction the step itself. It's better to wrap
with transaction an injected functions.

```pycon

>>> from app.transactions import atomic
>>> from app.repositories import lock_item, charge_money
>>> from app.messages import send_notification

>>> purchase = Purchase(atomic(lock_item), atomic(charge_money), send_notification)

>>> purchase.make(user_id=1)
BEGIN TRANSACTION;
UPDATE 'items';
COMMIT TRANSACTION;
BEGIN TRANSACTION;
UPDATE 'balance';
COMMIT TRANSACTION;

```

## Whole story

...

```pycon

>>> @dataclass
... class Transactional:
...
...     @story
...     def do(I):
...         I.begin
...         I.wrapped
...         I.end
...
...     def begin(self, ctx):
...         self.start_transaction()
...         return Success()
...
...     def end(self, ctx):
...         self.end_transaction()
...         return Success()
...
...     start_transaction: Callable
...     wrapped: story
...     end_transaction: Callable

>>> from app.transactions import start_transaction, end_transaction, cancel_transaction

>>> class Persistance:
...
...     def __init__(self):
...         self.started = False
...         self.commited = False
...
...     def start_transaction(self):
...         self.started = True
...         start_transaction()
...
...     def end_transaction(self):
...         self.commited = True
...         end_transaction()
...
...     def finalize(self):
...         if self.started and not self.commited:
...             cancel_transaction()

>>> persistance = Persistance()
>>> purchase = Purchase(lock_item, charge_money, send_notification)
>>> transactional = Transactional(persistance.start_transaction, purchase.make, persistance.end_transaction)

>>> transactional.do.run(user_id=1)
BEGIN TRANSACTION;
UPDATE 'items';
UPDATE 'balance';
COMMIT TRANSACTION;
Success()

>>> persistance.finalize()

>>> persistance = Persistance()
>>> purchase = Purchase(lock_item, charge_money, send_notification)
>>> transactional = Transactional(persistance.start_transaction, purchase.make, persistance.end_transaction)
>>> transactional.do.run(user_id=2)
BEGIN TRANSACTION;
UPDATE 'items';
UPDATE 'balance';
Failure()

>>> persistance.finalize()
ROLLBACK TRANSACTION;

```
