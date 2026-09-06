"""State monad: pure stateful computation without mutation.

State[S, A] = S → (S, A)

The State monad threads state through a pipeline without mutation.
Each step reads and/or modifies the state, and the final state
is returned alongside the result.

Use cases:
    - Parsers (state = remaining input)
    - Interpreters (state = variable bindings)
    - ID generators (state = counter)
    - Game logic (state = game world)
"""

from funstruct.monad.state import State


# ── Example 1: Counter (state = int) ────────────────────────────────


def next_id() -> State:
    """Generate the next ID, incrementing the counter."""
    return State(lambda s: (s + 1, s))


@State.do
def allocate_three():
    """Allocate three sequential IDs."""
    a = yield next_id()
    b = yield next_id()
    c = yield next_id()
    return (a, b, c)


# ── Example 2: Stack machine (state = list) ─────────────────────────


def push(value) -> State:
    return State(lambda stack: ([value] + stack, None))


def pop() -> State:
    return State(lambda stack: (stack[1:], stack[0]))


def peek() -> State:
    return State(lambda stack: (stack, stack[0]))


@State.do
def stack_program():
    """Push, pop, peek — all purely functional."""
    yield push(10)
    yield push(20)
    yield push(30)
    top = yield pop()
    second = yield peek()
    return f"popped {top}, next is {second}"


# ── Example 3: Symbol table (state = dict) ───────────────────────────


def assign(name: str, value) -> State:
    return State(lambda env: ({**env, name: value}, None))


def lookup(name: str) -> State:
    return State(lambda env: (env, env.get(name)))


@State.do
def interpreter():
    """Simple interpreter that assigns and looks up variables."""
    yield assign("x", 10)
    yield assign("y", 20)
    x = yield lookup("x")
    y = yield lookup("y")
    yield assign("result", x + y)
    result = yield lookup("result")
    return result


def main():
    print("=== State monad: pure stateful computation ===\n")

    # Counter
    final_state, ids = allocate_three().run(100)
    print(f"  Counter: IDs = {ids}, final counter = {final_state}")

    # Stack
    final_stack, result = stack_program().run([])
    print(f"  Stack:   {result}, remaining = {final_stack}")

    # Symbol table
    final_env, result = interpreter().run({})
    print(f"  Interp:  result = {result}, env = {final_env}")

    print("\n  No mutation — state threads through .run(initial).")
    print("  Each step is a pure function S → (S, A).")

    # Compose with bind
    print("\n=== Bind chain ===\n")
    result = next_id().bind(lambda a: next_id().map(lambda b: (a, b)))
    state, pair = result.run(0)
    print(f"  Two IDs: {pair}, counter = {state}")


if __name__ == "__main__":
    main()
