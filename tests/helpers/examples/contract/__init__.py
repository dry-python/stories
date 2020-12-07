from operator import itemgetter

from stories import arguments
from stories import story


# Helper functions.


class Integer:
    def __call__(self, value):
        if isinstance(value, int):
            return value, None
        elif isinstance(value, str) and value.isdigit():
            return int(value), None
        else:
            return None, "Invalid value"

    def __repr__(self):
        return "Integer()"


class String:
    def __call__(self, value):
        if isinstance(value, str):
            return value, None
        else:
            return None, "Invalid value"

    def __repr__(self):
        return "String()"


class List:
    def __init__(self, f):
        self.f = f

    def __call__(self, value):
        if isinstance(value, list):
            new = list(map(self.f, value))
            if any(map(itemgetter(1), new)):
                return None, "Invalid value"
            else:
                return list(map(itemgetter(0), new)), None
        else:
            return None, "Invalid value"

    def __repr__(self):
        return "List(" + repr(self.f) + ")"


class Dict:
    def __init__(self, k, v):
        self.k = k
        self.v = v

    def __call__(self, value):
        if isinstance(value, dict):
            new_key = list(map(self.k, value.keys()))
            new_value = list(map(self.v, value.values()))
            if any(map(itemgetter(1), new_key)) or any(map(itemgetter(1), new_value)):
                return None, "Invalid value"
            else:
                return {self.k(x)[0]: self.v(y)[0] for x, y in value.items()}, None
        else:
            return None, "Invalid value"

    def __repr__(self):
        return "Dict(" + repr(self.k) + ", " + repr(self.v) + ")"


# FIXME: Add multiline error so we could check text wrap indent was applied to the
# error message.


# Child base classes.


class Child:
    @story
    def x(I):
        I.one

    x.contract({"foo": Integer(), "bar": List(Integer()), "baz": Integer()})


class ChildWithNull:
    @story
    def x(I):
        I.one


class ChildWithShrink:
    @story
    def x(I):
        I.one

    x.contract({"baz": Integer()})


class ChildAlias:
    @story
    def x(I):
        I.one

    x.contract(
        {
            "foo": Dict(String(), String()),
            "bar": Dict(String(), String()),
            "baz": Dict(String(), Integer()),
        }
    )


class ParamChild:
    @story
    @arguments("foo", "bar")
    def x(I):
        I.one

    x.contract({"foo": Integer(), "bar": List(Integer()), "baz": Integer()})


class ParamChildWithNull:
    @story
    @arguments("foo", "bar")
    def x(I):
        I.one


class ParamChildWithShrink:
    @story
    @arguments("foo", "bar", "baz")
    def x(I):
        I.one

    x.contract({"baz": Integer()})


class ParamChildAlias:
    @story
    @arguments("foo", "bar", "baz")
    def x(I):
        I.one

    x.contract(
        {
            "foo": Dict(String(), String()),
            "bar": Dict(String(), String()),
            "baz": Dict(String(), Integer()),
        }
    )


# Next child base classes.


class NextChildWithSame:
    @story
    def y(I):
        I.one

    y.contract({"foo": Integer(), "bar": List(Integer()), "baz": Integer()})


class NextParamChildWithString:
    @story
    @arguments("foo", "bar")
    def y(I):
        I.two

    y.contract({"foo": String(), "bar": List(String())})


# Parent base classes.


class Parent:
    @story
    def a(I):
        I.before
        I.x
        I.after


Parent.a.contract({"ham": Integer(), "eggs": Integer(), "beans": Integer()})


class ParentWithNull:
    @story
    def a(I):
        I.before
        I.x
        I.after


class ParentWithSame:
    @story
    def a(I):
        I.before
        I.x
        I.after


ParentWithSame.a.contract({"foo": Integer(), "bar": List(Integer()), "baz": Integer()})


class SequentialParent:
    @story
    def a(I):
        I.before
        I.x
        I.y
        I.after

    a.contract({})


class ParamParent:
    @story
    @arguments("ham", "eggs")
    def a(I):
        I.before
        I.x
        I.after


ParamParent.a.contract({"ham": Integer(), "eggs": Integer(), "beans": Integer()})


class ParamParentWithNull:
    @story
    @arguments("ham", "eggs")
    def a(I):
        I.before
        I.x
        I.after


class ParamParentWithSame:
    @story
    @arguments("foo", "bar", "baz")
    def a(I):
        I.before
        I.after


ParamParentWithSame.a.contract(
    {"foo": Integer(), "bar": List(Integer()), "baz": Integer()}
)


class ParamParentWithSameWithString:
    @story
    @arguments("foo", "bar")
    def a(I):
        I.before
        I.x
        I.after


ParamParentWithSameWithString.a.contract({"foo": String(), "bar": List(String())})


# Root base classes.


class Root:
    @story
    def i(I):
        I.start
        I.a
        I.finish


Root.i.contract({"fizz": Integer(), "buzz": Integer()})


class RootWithSame:
    @story
    def i(I):
        I.start
        I.a
        I.finish


RootWithSame.i.contract({"foo": Integer(), "bar": List(Integer()), "baz": Integer()})


class SequentialRoot:
    @story
    def i(I):
        I.start
        I.a
        I.b
        I.finish


SequentialRoot.i.contract({"fizz": Integer(), "buzz": Integer()})


class ParamRoot:
    @story
    @arguments("fizz")
    def i(I):
        I.start
        I.a
        I.finish


ParamRoot.i.contract({"fizz": Integer(), "buzz": Integer()})
