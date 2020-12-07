from examples.contract import *  # noqa: F401, F403
from stories import Success


# Mixins.


class NormalMethod:
    def one(self, ctx):
        return Success()


class StringMethod:
    def one(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()


class WrongMethod:
    def one(self, ctx):
        ctx.foo = "<boom>"


class UnknownMethod:
    def one(self, ctx):
        ctx.spam = "0"


class ExceptionMethod:
    def one(self, ctx):
        raise Exception


class AliasMethod:
    def one(self, ctx):
        value = {"key": "1"}
        ctx.foo = value
        ctx.bar = value
        ctx.baz = value
        return Success()


# Next child mixins.


class NormalNextMethod:
    def two(self, ctx):
        return Success()


# Parent mixins.


class NormalParentMethod:
    def before(self, ctx):
        return Success()

    def after(self, ctx):
        return Success()


class StringParentMethod:
    def before(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()

    def after(self, ctx):
        return Success()


class ExceptionParentMethod:
    def before(self, ctx):
        raise Exception

    def after(self, ctx):
        return Success()


# Root mixins.


class NormalRootMethod:
    def start(self, ctx):
        return Success()

    def finish(self, ctx):
        return Success()


class StringRootMethod:
    def start(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()

    def finish(self, ctx):
        return Success()


class StringWideRootMethod:
    def start(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        ctx.baz = "1"
        return Success()

    def finish(self, ctx):
        return Success()


class ExceptionRootMethod:
    def start(self, ctx):
        raise Exception

    def finish(self, ctx):
        return Success()
