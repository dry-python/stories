import pytest

from helpers import make_collector
from stories.exceptions import ContextContractError


# TODO: Show collected arguments of the story composition in the error
# messages.
#
# TODO: Show violation values in validation error messages.
#
# TODO: Write correct and verbose docstrings for each test in this
# module.
#
# TODO: Document test class names in the contribution guide.


def test_assign_existed_variables(r, m):
    """We can not write a variable with the same name to the context twice."""

    class T(m.ParamChildWithNull, m.StringMethod):
        pass

    class J(m.ParentWithNull, m.StringParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
This variable is already present in the context: 'foo'

Function returned value: T.one

Use a different name for context attribute.

T.x
  one

Context:
  bar: [2]  # Story argument
  foo: 1    # Story argument
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(foo=1, bar=[2])
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(foo=1, bar=[2])
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
This variable is already present in the context: 'foo'

Function returned value: T.one

Use a different name for context attribute.

J.a
  before
  x (T.x)
    one

Context:
  foo: '1'    # Set by J.before
  bar: ['2']  # Set by J.before
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)()
    assert str(exc_info.value) == expected


def test_context_variables_normalization(r, m):
    """We apply normalization to the context variables, if story defines context
    contract.

    If story step returns a string holding a number, we should store a number in the
    context.

    """

    class T(m.Child, m.StringMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    getter = make_collector()
    r(T().x)()
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(T().x.run)()
    assert getter().foo == 1
    assert getter().bar == [2]

    # Substory DI.

    getter = make_collector()
    r(J().a)()
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(J().a.run)()
    assert getter().foo == 1
    assert getter().bar == [2]


def test_context_variables_normalization_conflict(r, m):
    """More than one substory can declare an argument with the same name.

    This means validators of both substories should return the same result.

    """

    # FIXME: Normalization conflict can consist of two
    # variables.  The first variable can be set by one
    # substory.  The second variable can be set by
    # another substory.

    class T(m.ParamChild, m.NormalMethod):
        pass

    class E(m.NextParamChildWithString, m.NormalNextMethod):
        pass

    class J(m.SequentialParent, m.StringParentMethod):
        def __init__(self):
            self.x = T().x
            self.y = E().y

    # Substory DI.

    expected = """
These arguments have normalization conflict: 'foo'

E.y:
 - foo: '1'

T.x:
 - foo: 1

Contract:
  foo:
    String()  # Argument of E.y
    Integer()  # Argument of T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)()
    assert str(exc_info.value) == expected


def test_story_arguments_normalization(r, m):
    """We apply normalization to the story arguments, if story defines context contract.

    If story was called with a string argument holding a number, we should store a
    number in the context.

    """

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.ParamParent, m.StringParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    getter = make_collector()
    r(T().x)(foo="1", bar=["2"])
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(T().x.run)(foo="1", bar=["2"])
    assert getter().foo == 1
    assert getter().bar == [2]

    # Substory DI.

    getter = make_collector()
    r(J().a)(ham="1", eggs="2")
    assert getter().ham == 1
    assert getter().eggs == 2

    getter = make_collector()
    r(J().a.run)(ham="1", eggs="2")
    assert getter().ham == 1
    assert getter().eggs == 2


def test_story_arguments_normalization_many_levels(r, m):
    """We apply normalization to the story arguments on any levels of story
    composition."""

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.ParamParent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    class F(m.ParamRoot, m.NormalRootMethod):
        def __init__(self):
            self.a = J().a

    # Substory DI.

    getter = make_collector()
    r(J().a)(ham="1", eggs="2", foo="3", bar=["4"])
    assert getter().ham == 1
    assert getter().eggs == 2
    assert getter().foo == 3
    assert getter().bar == [4]

    getter = make_collector()
    r(J().a.run)(ham="1", eggs="2", foo="3", bar=["4"])
    assert getter().ham == 1
    assert getter().eggs == 2
    assert getter().foo == 3
    assert getter().bar == [4]

    getter = make_collector()
    r(F().i)(fizz="0", ham="1", eggs="2", foo="3", bar=["4"])
    assert getter().fizz == 0
    assert getter().ham == 1
    assert getter().eggs == 2
    assert getter().foo == 3
    assert getter().bar == [4]

    getter = make_collector()
    r(F().i.run)(fizz="0", ham="1", eggs="2", foo="3", bar=["4"])
    assert getter().fizz == 0
    assert getter().ham == 1
    assert getter().eggs == 2
    assert getter().foo == 3
    assert getter().bar == [4]


def test_story_arguments_normalization_conflict(r, m):
    """Story and substory can have an argument with the same name.

    They both will define validators for this argument.  If normalization result of both
    contracts will mismatch we should raise an error.

    """

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.ParamParentWithSameWithString, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Substory DI.

    expected = """
These arguments have normalization conflict: 'bar', 'foo'

J.a:
 - bar: ['2']
 - foo: '1'

T.x:
 - bar: [2]
 - foo: 1

Contract:
  bar:
    List(String())  # Argument of J.a
    List(Integer())  # Argument of T.x
  foo:
    String()  # Argument of J.a
    Integer()  # Argument of T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(foo="1", bar=["2"])
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(foo="1", bar=["2"])
    assert str(exc_info.value) == expected


def test_context_variables_validation(r, m):
    """We apply validators to the context variables, if story defines context
    contract."""

    class T(m.Child, m.WrongMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
This variable violates context contract: 'foo'

Function returned value: T.one

Violations:

foo:
  '<boom>'
  Invalid value

Contract:
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)()
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
This variable violates context contract: 'foo'

Function returned value: T.one

Violations:

foo:
  '<boom>'
  Invalid value

Contract:
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)()
    assert str(exc_info.value) == expected


def test_story_arguments_validation(r, m):
    """We apply validators to the story arguments, if story defines context contract.

    This is check performed during story call, not execution.

    """

    class T(m.ParamChild, m.ExceptionMethod):
        pass

    class J(m.ParamParent, m.ExceptionParentMethod):
        def __init__(self):
            class T(m.Child, m.NormalMethod):
                pass

            self.x = T().x

    # Simple.

    expected = """
These arguments violates context contract: 'bar', 'foo'

Story method: T.x

Violations:

bar:
  ['<boom>']
  Invalid value

foo:
  '<boom>'
  Invalid value

Contract:
  bar: List(Integer())  # Argument of T.x
  foo: Integer()  # Argument of T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(foo="<boom>", bar=["<boom>"])
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(foo="<boom>", bar=["<boom>"])
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments violates context contract: 'eggs', 'ham'

Story method: J.a

Violations:

eggs:
  '<boom>'
  Invalid value

ham:
  '<boom>'
  Invalid value

Contract:
  eggs: Integer()  # Argument of J.a
  ham: Integer()  # Argument of J.a
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(ham="<boom>", eggs="<boom>")
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(ham="<boom>", eggs="<boom>")
    assert str(exc_info.value) == expected


def test_story_arguments_validation_many_levels(r, m):
    """We apply contract validation to the story arguments on any levels of story
    composition."""

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    class F(m.Root, m.ExceptionRootMethod):
        def __init__(self):
            self.a = J().a

    # Substory DI.

    expected = """
These arguments violates context contract: 'foo'

Story method: F.i

Violations:

foo:
  '<boom>'
  Invalid value

Contract:
  foo: Integer()  # Argument of T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(F().i)(foo="<boom>", bar=[1])
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(F().i.run)(foo="<boom>", bar=[1])
    assert str(exc_info.value) == expected


def test_composition_contract_variable_conflict(r, m):
    """Story and substory contracts can not declare the same variable twice."""

    class T(m.Child, m.NormalMethod):
        pass

    class J(m.ParentWithSame, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Substory DI.

    expected = """
Repeated variables can not be used in a story composition.

Variables repeated in both context contracts: 'bar', 'baz', 'foo'

Story method: J.a

Substory method: T.x

Use variables with different names.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a
    assert str(exc_info.value) == expected


def test_composition_contract_variable_conflict_many_levels(r, m):
    """Story and substory contracts can not declare the same variable twice."""

    class T(m.Child, m.NormalMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    class F(m.RootWithSame, m.NormalRootMethod):
        def __init__(self):
            self.a = J().a

    # Substory DI.

    expected = """
Repeated variables can not be used in a story composition.

Variables repeated in both context contracts: 'bar', 'baz', 'foo'

Story method: F.i

Substory method: T.x

Use variables with different names.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        F().i
    assert str(exc_info.value) == expected


def test_composition_contract_variable_conflict_sequential(r, m):
    """Story and substory contracts can not declare the same variable twice."""

    class T(m.Child, m.NormalMethod):
        pass

    class E(m.NextChildWithSame, m.NormalMethod):
        pass

    class J(m.SequentialParent, m.StringParentMethod):
        def __init__(self):
            self.x = T().x
            self.y = E().y

    # Substory DI.

    expected = """
Repeated variables can not be used in a story composition.

Variables repeated in both context contracts: 'bar', 'baz', 'foo'

Story method: T.x

Substory method: E.y

Use variables with different names.
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a
    assert str(exc_info.value) == expected


def test_composition_incompatible_contract_types(r, m):
    """Deny to use different types in the story composition."""

    class T(m.Child, m.NormalMethod):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Substory DI.

    expected = """
Story and substory context contracts has incompatible types:

Story method: J.a

Story context contract: None

Substory method: T.x

Substory context contract: dict
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a
    assert str(exc_info.value) == expected


def test_unknown_context_variable(r, m):
    """Step can't use Success argument name which was not specified in the contract."""

    class T(m.Child, m.UnknownMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
This variable was not defined in the context contract: 'spam'

Function assigned value: T.one

Use a different name for context attribute or add this name to the contract.

Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)()
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
This variable was not defined in the context contract: 'spam'

Function assigned value: T.one

Use a different name for context attribute or add this name to the contract.

Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)()
    assert str(exc_info.value) == expected


def test_unknown_story_arguments_with_null(r, m):
    """Allow to pass known only story and substory arguments to the call."""

    class T(m.ParamChildWithNull, m.NormalMethod):
        pass

    class J(m.ParamParentWithNull, m.NormalParentMethod):
        def __init__(self):
            class T(m.ChildWithNull, m.NormalMethod):
                pass

            self.x = T().x

    # Simple.

    expected = """
These arguments are unknown: baz, fox

Story method: T.x

Contract:
  bar  # Argument of T.x
  foo  # Argument of T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments are unknown: beans, fox

Story method: J.a

Contract:
  eggs  # Argument of J.a
  ham  # Argument of J.a
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(beans=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(beans=1, fox=2)
    assert str(exc_info.value) == expected


def test_unknown_story_arguments(r, m):
    """Allow to pass known only story and substory arguments to the call."""

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.ParamParent, m.NormalParentMethod):
        def __init__(self):
            class T(m.Child, m.NormalMethod):
                pass

            self.x = T().x

    # Simple.

    expected = """
These arguments are unknown: baz, fox

Story method: T.x

Contract:
  bar: List(Integer())  # Argument of T.x
  foo: Integer()  # Argument of T.x
  baz: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments are unknown: beans, fox

Story method: J.a

Contract:
  eggs: Integer()  # Argument of J.a
  ham: Integer()  # Argument of J.a
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(beans=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(beans=1, fox=2)
    assert str(exc_info.value) == expected


def test_unknown_story_arguments_with_empty_with_null(r, m):
    """Deny any arguments in the call, if story and substory has no arguments
    specified."""

    class T(m.ChildWithNull, m.NormalMethod):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These arguments are unknown: baz, fox

Story method: T.x

Contract()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments are unknown: beans, fox

Story method: J.a

Contract()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(beans=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(beans=1, fox=2)
    assert str(exc_info.value) == expected


def test_unknown_story_arguments_with_empty(r, m):
    """Deny any arguments in the call, if story and substory has no arguments
    specified."""

    class T(m.Child, m.NormalMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These arguments are unknown: baz, fox

Story method: T.x

Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  foo: Integer()  # Variable in T.x
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)(baz=1, fox=2)
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments are unknown: beans, fox

Story method: J.a

Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
  eggs: Integer()  # Variable in J.a
  foo: Integer()  # Variable in T.x
  ham: Integer()  # Variable in J.a
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)(beans=1, fox=2)
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)(beans=1, fox=2)
    assert str(exc_info.value) == expected


def test_require_story_arguments_present_in_context(r, m):
    """Check story and substory arguments are present in the context."""

    class T(m.ParamChildWithNull, m.NormalMethod):
        pass

    class J(m.ParentWithNull, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These variables are missing from the context: bar, foo

Story method: T.x

Story arguments: foo, bar

T.x

Context()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x)()  # FIXME: This should be arguments error (not substory call error).
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(T().x.run)()
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These variables are missing from the context: bar, foo

Story method: T.x

Story arguments: foo, bar

J.a
  before
  x (T.x)

Context()
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a)()
    assert str(exc_info.value) == expected

    with pytest.raises(ContextContractError) as exc_info:
        r(J().a.run)()
    assert str(exc_info.value) == expected


def test_parent_steps_set_story_arguments(r, m):
    """Steps of parent stories should be able to set child stories arguments with
    `Success` marker keyword arguments."""

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.Parent, m.StringParentMethod):
        def __init__(self):
            self.x = T().x

    class R(m.Root, m.StringRootMethod, m.Parent, m.NormalParentMethod, T):
        pass

    class F(m.Root, m.StringRootMethod):
        def __init__(self):
            class J(m.Parent, m.NormalParentMethod):
                def __init__(self):
                    self.x = T().x

            self.a = J().a

    # Substory DI.

    getter = make_collector()
    r(J().a)()
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(J().a.run)()
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(F().i)()
    assert getter().foo == 1
    assert getter().bar == [2]

    getter = make_collector()
    r(F().i.run)()
    assert getter().foo == 1
    assert getter().bar == [2]


def test_sequential_story_steps_set_story_arguments(r, m):
    """There are a few sequential substories with one common parent story.

    One substory should be able to set variable to provide an argument to the next
    sequential story.

    """

    class T(m.ChildWithShrink, m.StringMethod):
        pass

    class E(m.NextParamChildWithString, m.NormalNextMethod):
        pass

    class J(m.SequentialParent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x
            self.y = E().y

    # Substory DI.

    getter = make_collector()
    r(J().a)()
    assert getter().foo == "1"
    assert getter().bar == ["2"]

    getter = make_collector()
    r(J().a.run)()
    assert getter().foo == "1"
    assert getter().bar == ["2"]


def test_arguments_should_be_declared_in_contract(r, m):
    """We should require all story arguments to be declared in the context contract."""

    class T(m.ParamChildWithShrink, m.NormalMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # Simple.

    expected = """
These arguments should be declared in the context contract: bar, foo

Story method: T.x

Story arguments: foo, bar, baz
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        T().x
    assert str(exc_info.value) == expected

    # Substory DI.

    expected = """
These arguments should be declared in the context contract: bar, foo

Story method: T.x

Story arguments: foo, bar, baz
    """.strip()

    with pytest.raises(ContextContractError) as exc_info:
        J().a
    assert str(exc_info.value) == expected


# Aliases.


def test_story_variable_alias_normalization_store_same_object(r, m):
    """When story step sets a set of variables some of them are aliases of each other.

    If the type and the value of alias are equal to the origin value, we should preserve
    the same reference to the value.

    """

    class T(m.ChildAlias, m.AliasMethod):
        pass

    # Simple.

    getter = make_collector()
    r(T().x)()
    assert getter().foo is getter().bar
    assert getter().foo == {"key": "1"}
    assert getter().bar == {"key": "1"}
    assert getter().foo is not getter().baz
    assert getter().bar is not getter().baz
    assert getter().baz == {"key": 1}

    getter = make_collector()
    r(T().x.run)()
    assert getter().foo is getter().bar
    assert getter().foo == {"key": "1"}
    assert getter().bar == {"key": "1"}
    assert getter().foo is not getter().baz
    assert getter().bar is not getter().baz
    assert getter().baz == {"key": 1}

    # FIXME: Substory DI.


def test_story_argument_alias_normalization_store_same_object(r, m):
    """When story has a set of arguments some of them are aliases of each other.

    If the type and the value of alias are equal to the origin value, we should preserve
    the same reference to the value.

    """

    class T(m.ParamChildAlias, m.NormalMethod):
        pass

    # Simple.

    value = {"key": "1"}

    getter = make_collector()
    r(T().x)(foo=value, bar=value, baz=value)
    assert getter().foo is getter().bar
    assert getter().foo == {"key": "1"}
    assert getter().bar == {"key": "1"}
    assert getter().foo is not getter().baz
    assert getter().bar is not getter().baz
    assert getter().baz == {"key": 1}

    getter = make_collector()
    r(T().x.run)(foo=value, bar=value, baz=value)
    assert getter().foo is getter().bar
    assert getter().foo == {"key": "1"}
    assert getter().bar == {"key": "1"}
    assert getter().foo is not getter().baz
    assert getter().bar is not getter().baz
    assert getter().baz == {"key": 1}

    # FIXME: Substory DI.


# Representation.


def test_story_contract_representation_with_spec(r, m):
    """Show collected story composition contract as mounted story attribute."""

    class T(m.Child, m.StringMethod):
        pass

    class J(m.Parent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    class F(m.Root, m.NormalRootMethod):
        def __init__(self):
            self.a = J().a

    # Simple.

    expected = """
Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  foo: Integer()  # Variable in T.x
    """.strip()

    assert repr(T().x.contract) == expected

    # Substory DI.

    expected = """
Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
  eggs: Integer()  # Variable in J.a
  foo: Integer()  # Variable in T.x
  ham: Integer()  # Variable in J.a
    """.strip()

    assert repr(J().a.contract) == expected

    # Hierarchy.

    expected = """
Contract:
  bar: List(Integer())  # Variable in T.x
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
  buzz: Integer()  # Variable in F.i
  eggs: Integer()  # Variable in J.a
  fizz: Integer()  # Variable in F.i
  foo: Integer()  # Variable in T.x
  ham: Integer()  # Variable in J.a
    """.strip()

    assert repr(F().i.contract) == expected


def test_story_contract_representation_with_spec_with_args(r, m):
    """Show collected story composition contract as mounted story attribute.

    We show each story arguments.

    """

    class T(m.ParamChild, m.StringMethod):
        pass

    class J(m.ParamParent, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    class F(m.ParamRoot, m.NormalRootMethod):
        def __init__(self):
            self.a = J().a

    # Simple.

    expected = """
Contract:
  bar: List(Integer())  # Argument of T.x
  foo: Integer()  # Argument of T.x
  baz: Integer()  # Variable in T.x
    """.strip()

    assert repr(T().x.contract) == expected

    # Substory DI.

    expected = """
Contract:
  bar: List(Integer())  # Argument of T.x
  eggs: Integer()  # Argument of J.a
  foo: Integer()  # Argument of T.x
  ham: Integer()  # Argument of J.a
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
    """.strip()

    assert repr(J().a.contract) == expected

    # Hierarchy.

    expected = """
Contract:
  bar: List(Integer())  # Argument of T.x
  eggs: Integer()  # Argument of J.a
  fizz: Integer()  # Argument of F.i
  foo: Integer()  # Argument of T.x
  ham: Integer()  # Argument of J.a
  baz: Integer()  # Variable in T.x
  beans: Integer()  # Variable in J.a
  buzz: Integer()  # Variable in F.i
    """.strip()

    assert repr(F().i.contract) == expected


def test_story_contract_representation_with_spec_with_args_conflict(r, m):
    """Show collected story composition contract as mounted story attribute.

    We show each story arguments in multiline mode if the same name was declared in
    multiple substories.

    """

    class T(m.ParamChild, m.NormalMethod):
        pass

    class J(m.ParamParentWithSameWithString, m.NormalParentMethod):
        def __init__(self):
            self.x = T().x

    # FIXME: Implement this.
    #
    # class F(..., m.NormalRootMethod):
    #     def __init__(self):
    #         self.a = J().a

    # Substory DI.

    expected = """
Contract:
  bar:
    List(String())  # Argument of J.a
    List(Integer())  # Argument of T.x
  foo:
    String()  # Argument of J.a
    Integer()  # Argument of T.x
  baz: Integer()  # Variable in T.x
    """.strip()

    assert repr(J().a.contract) == expected

    #     expected = """
    # Contract:
    #   fizz: ...  # F.i argument
    #   ham: ...   # J.a argument
    #   eggs: ...  # J.a argument
    #   foo: ...   # T.x argument
    #   bar: ...   # T.x argument
    #   buzz: ...  # F.i variable
    #   beans: ... # J.a variable
    #   baz: ...   # T.x variable
    #     """.strip()
    #
    #     assert repr(F().i.contract) == expected
