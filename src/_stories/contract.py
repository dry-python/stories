from operator import itemgetter

from _stories.exceptions import ContextContractError


# FIXME: Handle protocol extension.  There should be way to say in the
# substory contract "this variable should be an integer" and in
# addition in the story "this integer should be greater than 7".  This
# way we also can require a certain substory to declare context
# variable for parent story.
#
# FIXME: Add fix suggestion to the bottom of the error message.
#
# FIXME: Support custom validation of complex relationships.  For
# example, `@pydantic.validator` of `password2` depends on
# `password1`.
#
# FIXME: Check that contracts collisions are checked in the situation:
#
# story
#   substory
#     substory with variable declaration
#   substory with this variable as an argument
#
# FIXME: Depending of the level of nesting the same substory can
# occurred multiple times at one argument in the contract
# representation.
#
# defaults:
#   typing.Union[typing.Dict[str, str], NoneType]  # Argument of ProcessImages.process
#   typing.Union[typing.Dict[str, str], NoneType]  # Argument of ProcessImages.process
#   typing.Union[typing.Dict[str, str], NoneType]  # Argument of ProcessImages.process
# raw_urls:
#   str  # Argument of FetchURLPreviews.fetch
#   str  # Argument of FetchURLPreviews.fetch
# files:
#   typing.Dict[str, typing.Union[str, int, typing.Any]]  # Argument of ProcessVideos.process  # noqa: E501
#   typing.Dict[str, typing.Union[str, int, typing.Any]]  # Argument of ProcessImages.process  # noqa: E501
#   typing.Dict[str, typing.Union[str, int, typing.Any]]  # Argument of ProcessImages.process  # noqa: E501
#   typing.Dict[str, typing.Union[str, int, typing.Any]]  # Argument of ProcessImages.process  # noqa: E501
#
# FIXME: Fix pydantic error messages.
#
# In [1]: class Context(pydantic.BaseModel):
#    ...:     files: typing.Dict[str, typing.Dict[str, typing.Union[str, int, typing.BinaryIO]]]  # noqa: E501
#    ...:
#
# In [2]: Context(files={"a": {'name': B(name='test'), 'size': 1}})
# ---------------------------------------------------------------------------
# ValidationError: 3 validation errors
# files -> a -> name
#   str type expected (type=type_error.str)
# files -> a -> name
#   value is not a valid integer (type=type_error.integer)
# files -> a -> name
#   instance of BinaryIO expected (type=type_error.arbitrary_type; expected_arbitrary_type=BinaryIO)  # noqa: E501
#
# FIXME: Test all field representation for all supported libraries.
# I.e. Dict, List, Tuple, Integer, String, etc.
#
# FIXME: Alias validation creates new object for each alias.  So they
# became not aliases.
#
# FIXME: Parent story can't define an argument, if child story already
# defined variable with the same name.
#
# FIXME: When Success argument is broken we should show validator of
# what argument of what substory is broken.  Because it's really hard
# to track down it in a deep story composition.
#
# FIXME: Nested collision detector doesn't support identity check for
# neighbor substories.  Only parent-child for now.
#
# class Subs
#   @story
#   def foo(I):
#
#   @story
#   def bar(I):
#
#   @contract_in(Subs)
#   class Context:
#     bar: int
#
# class Parent:
#   @story
#   def quiz(I):
#     I.foo
#     I.bar   <--- `bar` will be treated as repeated variable.
#
# NOTE: `noqa` comments are not part of the program output.


def make_contract(cls_name, name, arguments, spec):
    __tracebackhide__ = True
    if spec is None:
        return NullContract(cls_name, name, arguments)
    elif isinstance(spec, dict):
        check_arguments_definitions(cls_name, name, arguments, spec)
        return SpecContract(cls_name, name, arguments, spec.copy())


def check_arguments_definitions(cls_name, name, arguments, spec):
    __tracebackhide__ = True
    undefined = set(arguments) - set(spec)
    if undefined:
        message = undefined_argument_template.format(
            undefined=", ".join(sorted(undefined)),
            cls=cls_name,
            method=name,
            arguments=", ".join(arguments),
        )
        raise ContextContractError(message)


class NullContract:
    def __init__(self, cls_name, name, arguments):
        self.cls_name = cls_name
        self.name = name
        self.arguments = arguments
        self.make_argset()

    def make_argset(self):
        self.argset = {
            arg: {(None, self.cls_name, self.name)} for arg in self.arguments
        }

    def check_story_call(self, kwargs, ns, seen):
        __tracebackhide__ = True
        # FIXME: Check required arguments here.
        unknown_arguments = set(kwargs) - set(self.argset)
        if unknown_arguments:
            message = unknown_argument_template.format(
                unknown=", ".join(sorted(unknown_arguments)),
                cls=self.cls_name,
                method=self.name,
                contract=self,
            )
            raise ContextContractError(message)
        return kwargs

    def check_substory_call(self, ctx, ns):
        __tracebackhide__ = True
        missed = set(self.arguments) - set(ns)
        if missed:
            message = missed_variable_template.format(
                missed=", ".join(sorted(missed)),
                cls=self.cls_name,
                method=self.name,
                arguments=", ".join(self.arguments),
                ctx=ctx,
            )
            raise ContextContractError(message)

    def check_assign_statement(self, method, ctx, ns, seen, name, value):
        __tracebackhide__ = True
        if name in ns:
            message = variable_override_template.format(
                variable=name,
                cls=method.__self__.__class__.__name__,
                method=method.__name__,
                ctx=ctx,
            )
            raise ContextContractError(message)
        return value

    def __repr__(self):
        return self.format_contract_fields(self.argset)

    def format_contract_fields(self, *fieldset):
        if not self.argset:
            return "Contract()"
        lines = ["Contract:"]
        arguments = sorted(
            field for fields in fieldset for field in fields if field in self.argset
        )
        for argument in arguments:
            # FIXME: This does not work for story composition when
            # many stories has the same argument.
            ((validator, cls_name, name),) = self.argset[argument]
            lines.append(f"  {argument}  # Argument of {cls_name}.{name}")
        return "\n".join(lines)


class SpecContract(NullContract):
    # FIXME: Deny empty disassembled spec.  If there is such need, we
    # should replace `NullContract` with empty `SpecContract`
    # ourselves.
    def __init__(self, cls_name, name, arguments, spec):
        self.spec = spec
        super().__init__(cls_name, name, arguments)
        self.make_declared()

    def make_argset(self):
        self.argset = {}
        for arg in self.arguments:
            self.argset[arg] = {(self.spec[arg], self.cls_name, self.name)}
            del self.spec[arg]

    def make_declared(self):
        self.declared = {
            variable: (self.cls_name, self.name, repr(validator))
            for variable, validator in self.spec.items()
        }

    def check_story_call(self, kwargs, ns, seen):
        __tracebackhide__ = True
        super().check_story_call(kwargs, ns, seen)
        result, errors = self.validate(kwargs, ns, seen)
        if errors:
            message = invalid_argument_template.format(
                variables=", ".join(map(repr, sorted(errors))),
                cls=self.cls_name,
                method=self.name,
                violations=format_violations(kwargs, errors),
                contract=self.format_contract_fields(errors),
            )
            raise ContextContractError(message)
        return result

    def check_assign_statement(self, method, ctx, ns, seen, name, value):
        __tracebackhide__ = True
        super().check_assign_statement(method, ctx, ns, seen, name, value)
        unknown = self.identify(name)
        if unknown:
            message = unknown_variable_template.format(
                unknown=name,
                cls=method.__self__.__class__.__name__,
                method=method.__name__,
                contract=self,
            )
            raise ContextContractError(message)
        normalized, errors = self.validate({name: value}, ns, seen)
        if errors:
            message = invalid_variable_template.format(
                variable=name,
                cls=method.__self__.__class__.__name__,
                method=method.__name__,
                violations=format_violations({name: value}, errors),
                contract=self.format_contract_fields(errors),
            )
            raise ContextContractError(message)
        return normalized[name]

    def identify(self, name):
        available = set(self.spec) | set(self.argset)
        unknown = name not in available
        return unknown

    def validate(self, kwargs, ns, seen):
        __tracebackhide__ = True
        result, errors, conflict = {}, {}, {}
        for key, value in kwargs.items():
            if key in self.spec:
                self.validate_spec(result, errors, ns, seen, key, value)
            else:
                self.validate_argset(result, errors, ns, seen, conflict, key, value)
        if conflict:
            conflict_vars = sorted({j for i in conflict.values() for j in i})
            message = normalization_conflict_template.format(
                conflict=", ".join(map(repr, conflict_vars)),
                results="\n\n".join(
                    "%s.%s:\n%s"
                    % (
                        cls,
                        method,
                        "\n".join(
                            " - {}: {!r}".format(i, result[i]) for i in sorted(result)
                        ),
                    )
                    for (cls, method), result in (
                        (i, conflict[i]) for i in sorted(conflict)
                    )
                ),
                contract=self.format_contract_fields(conflict_vars),
            )
            raise ContextContractError(message)
        return result, errors

    def validate_spec(self, result, errors, ns, seen, key, value):
        new_value, error = self.spec[key](value)
        if error:
            errors[key] = error
        else:
            self.assign_result(result, ns, seen, key, value, new_value)

    def validate_argset(self, result, errors, ns, seen, conflict, key, value):
        new_values, has_error = [], False
        for validator, cls_name, name in self.argset[key]:
            new_value, error = validator(value)
            if error:
                has_error = True
                errors[key] = error
            else:
                new_values.append((new_value, cls_name, name))
        if new_values:
            first, others = new_values[0], new_values[1:]
            for other in others:
                if first[0] != other[0]:
                    conflict.setdefault((first[1], first[2]), {})
                    conflict[(first[1], first[2])][key] = first[0]
                    conflict.setdefault((other[1], other[2]), {})
                    conflict[(other[1], other[2])][key] = other[0]
        if not has_error:
            self.assign_result(result, ns, seen, key, value, new_value)

    def assign_result(self, result, ns, seen, key, value, new_value):
        for seen_key, seen_value in seen:
            if value is seen_value:
                # It will be `ns` if we are validating previous
                # assignment.  It will be `result` if we are validating
                # story call arguments.
                place = ns if seen_key in ns else result
                seen_new_value = place[seen_key]
                if (
                    type(new_value) is type(seen_new_value)
                    and new_value == seen_new_value
                ):
                    result[key] = seen_new_value
                    return
        result[key] = new_value
        seen.append((key, value))

    def __repr__(self):
        return self.format_contract_fields(self.argset, self.declared)

    def format_contract_fields(self, *fieldset):
        lines = ["Contract:"]
        arguments = sorted(
            field for fields in fieldset for field in fields if field in self.argset
        )
        for argument in arguments:
            validators = self.argset[argument]
            if len(validators) == 1:
                ((validator, cls_name, name),) = validators
                lines.append(
                    "  %s: %r  # Argument of %s.%s"
                    % (argument, validator, cls_name, name)
                )
            else:
                lines.append(f"  {argument}:")
                for validator in sorted(validators, key=itemgetter(1, 2)):
                    lines.append("    %r  # Argument of %s.%s" % validator)
        variables = sorted(
            field for fields in fieldset for field in fields if field in self.declared
        )
        for variable in variables:
            cls_name, name, field_name = self.declared[variable]
            lines.append(
                "  {}: {}  # Variable in {}.{}".format(
                    variable, field_name, cls_name, name
                )
            )
        return "\n".join(lines)


def format_violations(kwargs, errors):
    result = []
    for key in sorted(errors):
        result.append(key + ":")
        result.append("  " + repr(kwargs[key]))
        result.append("  " + errors[key])
        result.append("")
    return "\n".join(result).strip()


# Wrap.


def combine_contract(parent, child):
    if type(parent) is NullContract and type(child) is NullContract:
        combine_argsets(parent, child)
        return
    elif type(parent) is SpecContract and type(child) is SpecContract:
        repeated = set(parent.declared) & set(child.declared)
        if repeated:
            # FIXME: Repeated variables can occur in three different
            # classes.
            key = next(iter(repeated))
            message = incompatible_contracts_template.format(
                repeated=", ".join(map(repr, sorted(repeated))),
                cls=parent.declared[key][0],
                method=parent.declared[key][1],
                other_cls=child.declared[key][0],
                other_method=child.declared[key][1],
            )
            raise ContextContractError(message)
        combine_argsets(parent, child)
        combine_declared(parent, child)
    else:
        message = type_error_template.format(
            cls=parent.cls_name,
            method=parent.name,
            contract=format_contract(parent),
            other_cls=child.cls_name,
            other_method=child.name,
            other_contract=format_contract(child),
        )
        raise ContextContractError(message)


def combine_argsets(parent, child):
    for key in set(parent.argset) & set(child.argset):
        parent.argset[key].update(child.argset[key])
        child.argset[key].update(parent.argset[key])
    for key in set(parent.argset) - set(child.argset):
        child.argset[key] = parent.argset[key]
    for key in set(child.argset) - set(parent.argset):
        parent.argset[key] = child.argset[key]


def combine_declared(parent, child):
    parent.declared.update(child.declared)


def format_contract(contract):
    if type(contract) is SpecContract:
        return "dict"
    else:
        return None


def maybe_extend_downstream_argsets(methods, root):
    if type(root) is NullContract:
        return
    for _method, contract, _protocol in methods:
        combine_argsets(root, contract)


# Messages.


undefined_argument_template = """
These arguments should be declared in the context contract: {undefined}

Story method: {cls}.{method}

Story arguments: {arguments}
""".strip()


missed_variable_template = """
These variables are missing from the context: {missed}

Story method: {cls}.{method}

Story arguments: {arguments}

{ctx!r}
""".strip()


variable_override_template = """
This variable is already present in the context: {variable!r}

Function returned value: {cls}.{method}

Use a different name for context attribute.

{ctx!r}
""".strip()


unknown_variable_template = """
This variable was not defined in the context contract: {unknown!r}

Function assigned value: {cls}.{method}

Use a different name for context attribute or add this name to the contract.

{contract!r}
""".strip()


unknown_argument_template = """
These arguments are unknown: {unknown}

Story method: {cls}.{method}

{contract!r}
""".strip()


invalid_variable_template = """
This variable violates context contract: {variable!r}

Function returned value: {cls}.{method}

Violations:

{violations}

{contract}
""".strip()


invalid_argument_template = """
These arguments violates context contract: {variables}

Story method: {cls}.{method}

Violations:

{violations}

{contract}
""".strip()


incompatible_contracts_template = """
Repeated variables can not be used in a story composition.

Variables repeated in both context contracts: {repeated}

Story method: {cls}.{method}

Substory method: {other_cls}.{other_method}

Use variables with different names.
""".strip()


type_error_template = """
Story and substory context contracts has incompatible types:

Story method: {cls}.{method}

Story context contract: {contract}

Substory method: {other_cls}.{other_method}

Substory context contract: {other_contract}
""".strip()


normalization_conflict_template = """
These arguments have normalization conflict: {conflict}

{results}

{contract}
""".strip()
