# command-lists.sh - every command-name set the executor guard consults, defined once.
# Sourced, never run. Defines variables only; in_set and list_join (hook-io.sh) read them.
# Bash 3.2: plain arrays only.

# A shell found as the real command (after wrapper stripping) is denied outright: its own
# -c argument is not parsed as a nested command line.
SHELLS=(sh bash zsh ksh dash ash)

# Inline interpreters and scripting tools, denied for lead and judge regardless of arguments.
INTERPRETERS=(python python2 python3 node nodejs deno bun perl ed xargs)

# Wrappers strip_command_wrappers peels (see parse.sh). Each one needs its own case there.
# rtk is the output-filtering proxy a user hook rewrites commands through (`rtk proxy <cmd>`
# runs <cmd> unfiltered, bare `rtk <cmd>` filters it): either way <cmd> is what runs.
WRAPPERS=(env command exec nohup nice time timeout stdbuf rtk)

# Reserved words that open or close a compound command. strip_leading_keywords (parse.sh) drops
# them from the front of a segment so the command after them is the one classified:
# `then bash x` is `bash x`. A `for`, `select` or `case` header holds words, not commands.
SHELL_KEYWORDS=(if then elif else fi do done while until '!' esac)
SHELL_HEADERS=(for select case)

# zsh precommand modifiers: they run the next word as a command with different rules (no
# globbing, no spelling correction, builtins only). Lead and judge are denied them.
ZSH_PRECOMMANDS=(noglob nocorrect builtin)

# Commands that create, overwrite or move a file; denied for lead and judge.
WRITE_CMDS=(cp mv install touch mkdir truncate tee patch)

# What lead and judge may use Bash for. Printed in the interpreter denial; the guard does not
# allowlist these (everything not denied is allowed).
READONLY_CMDS=(grep "sed -n" "git log" "git diff" jq wc find cat head tail ls diff shellcheck)

# Commands whose heredoc body is harmless input rather than commands (see heredoc.sh).
# Space-delimited so a membership test is *" $name "*. `git:stdin` is the form
# heredoc_consumer prints for git commit/tag reading its message from stdin.
HEREDOC_READERS=" python python3 node cat jq tee wc sort uniq head tail grep diff git:stdin "

# git global options find_git_subcommand (parse.sh) steps over to reach the subcommand. An
# option in none of the three lists is unrecognized: lead and judge are refused it, the others
# skip it as a valueless flag.
#   SHORT_VALUE  the value is the next token (`-C dir`, `-c k=v`); git has no attached form.
#   VALUE        the value is the next token or attached (`--git-dir dir`, `--git-dir=dir`).
#   FLAG         takes no value (`--exec-path=dir` is also stepped over: it only prints or sets).
GIT_OPTS_SHORT_VALUE=(-C -c)
GIT_OPTS_VALUE=(--git-dir --work-tree --namespace --config-env --super-prefix --attr-source)
GIT_OPTS_FLAG=(--no-pager -P -p --paginate --bare --no-replace-objects --literal-pathspecs --glob-pathspecs --noglob-pathspecs --icase-pathspecs --no-optional-locks --exec-path --html-path --man-path --info-path --version -v --help -h)

# git subcommands that read their message from stdin with -F - (heredoc.sh).
GIT_STDIN_MESSAGE_SUBS=(commit tag)

# git subcommands that change tracked or staged file state; denied for lead and judge.
GIT_WRITE_SUBS=(add commit apply stash rm mv)

# The git tag forms lead and judge may use, as printed in the git tag denials. The rule that
# enforces them is the tag case in rules-readonly.sh; keep the two together.
GIT_TAG_READ_FORMS=("git tag" "-l/--list" "-n" "--contains" "--no-contains" "--points-at" "--merged" "--no-merged" "--sort" "--format" "-v/--verify")

# Package managers whose publish is denied.
PUBLISH_CMDS=(npm yarn pnpm)
