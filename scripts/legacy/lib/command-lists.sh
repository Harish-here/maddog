# command-lists.sh - every command-name set the executor guard consults, defined once.
# Sourced, never run. Defines variables only; in_set and list_join (hook-io.sh) read them.
# Bash 3.2: plain arrays only.

# A shell found as the real command (after wrapper stripping) is denied outright: its own
# -c argument is not parsed as a nested command line.
SHELLS=(sh bash zsh ksh dash ash)

# Inline interpreters and scripting tools, denied for lead and judge regardless of arguments.
INTERPRETERS=(python python2 python3 node nodejs deno bun perl ed xargs)

# Wrappers strip_command_wrappers peels (see parse.sh). Each one needs its own case there.
WRAPPERS=(env command exec nohup nice time timeout stdbuf)

# Commands that create, overwrite or move a file; denied for lead and judge.
WRITE_CMDS=(cp mv install touch mkdir truncate tee patch)

# What lead and judge may use Bash for. Printed in the interpreter denial; the guard does not
# allowlist these (everything not denied is allowed).
READONLY_CMDS=(grep "sed -n" "git log" "git diff" jq wc find cat head tail ls diff shellcheck)

# Commands whose heredoc body is harmless input rather than commands (see heredoc.sh).
# Space-delimited so a membership test is *" $name "*. `git:stdin` is the form
# heredoc_consumer prints for git commit/tag reading its message from stdin.
HEREDOC_READERS=" python python3 node cat jq tee wc sort uniq head tail grep diff git:stdin "

# git subcommands that read their message from stdin with -F - (heredoc.sh).
GIT_STDIN_MESSAGE_SUBS=(commit tag)

# git subcommands that change tracked or staged file state; denied for lead and judge.
GIT_WRITE_SUBS=(add commit apply stash rm mv)

# The git tag forms lead and judge may use, as printed in the git tag denials. The rule that
# enforces them is the tag case in rules-readonly.sh; keep the two together.
GIT_TAG_READ_FORMS=("git tag" "-l/--list" "-n" "--contains" "--no-contains" "--points-at" "--merged" "--no-merged" "--sort" "--format" "-v/--verify")

# Package managers whose publish is denied.
PUBLISH_CMDS=(npm yarn pnpm)
