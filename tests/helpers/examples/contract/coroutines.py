from examples.contract import *  # noqa: F401, F403
from stories import Success


# Mixins.


class NormalMethod:
    async def one(self, ctx):
        return Success()


class StringMethod:
    async def one(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()


class WrongMethod:
    async def one(self, ctx):
        ctx.foo = "<boom>"


class UnknownMethod:
    async def one(self, ctx):
        ctx.spam = "0"


class ExceptionMethod:
    async def one(self, ctx):
        raise Exception


class AliasMethod:
    async def one(self, ctx):
        value = {"key": "1"}
        ctx.foo = value
        ctx.bar = value
        ctx.baz = value
        return Success()


# Next child mixins.


class NormalNextMethod:
    async def two(self, ctx):
        return Success()


# Parent mixins.


class NormalParentMethod:
    async def before(self, ctx):
        return Success()

    async def after(self, ctx):
        return Success()


class StringParentMethod:
    async def before(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()

    async def after(self, ctx):
        return Success()


class ExceptionParentMethod:
    async def before(self, ctx):
        raise Exception

    async def after(self, ctx):
        return Success()


# Root mixins.


class NormalRootMethod:
    async def start(self, ctx):
        return Success()

    async def finish(self, ctx):
        return Success()


class StringRootMethod:
    async def start(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        return Success()

    async def finish(self, ctx):
        return Success()


class StringWideRootMethod:
    async def start(self, ctx):
        ctx.foo = "1"
        ctx.bar = ["2"]
        ctx.baz = "1"
        return Success()

    async def finish(self, ctx):
        return Success()


class ExceptionRootMethod:
    async def start(self, ctx):
        raise Exception

    async def finish(self, ctx):
        return Success()
