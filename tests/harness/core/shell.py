"""Read a shell command line as the steps it runs. Pure text; names no runtime.

A model often chains its steps in one call (`tail log > crash.log && rm app.lock
&& sh start.sh`). The order checks care about the steps, not the call, so agent
mode records one event per step. This is a quote-aware split, not a shell
parser: it does not look inside `$( )` or `( )`, and a `for ...; do ...; done`
loop splits into harmless pieces."""

STEP_BREAKS = ("&&", "||")


def split_shell(command: str) -> list[str]:
    """The steps of a command line, in order: split on `&&`, `||`, `;` and
    newlines outside quotes. A pipeline (`a | b`) stays one step."""
    steps: list[str] = []
    current: list[str] = []
    quote = None
    i = 0
    while i < len(command):
        ch = command[i]
        if quote:
            current.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(command):
                i += 1
                current.append(command[i])
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            current.append(ch)
        elif command.startswith(STEP_BREAKS, i):
            steps.append("".join(current))
            current = []
            i += 1  # the second character of the pair
        elif ch in ";\n":
            steps.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    steps.append("".join(current))
    return [step.strip() for step in steps if step.strip()]


def first_in_pipeline(step: str) -> str:
    """The command at the head of a pipeline: the text before the first `|` outside quotes."""
    quote = None
    for i, ch in enumerate(step):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "|":
            return step[:i].strip()
    return step.strip()
