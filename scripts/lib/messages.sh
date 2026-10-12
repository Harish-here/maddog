# messages.sh - every refusal and context text the hooks print, defined once.
# Sourced, never run. A text with no moving part is a MSG_* variable; one that names a
# command, flag, caller or target is a msg_* function that prints it. The static ones (used
# with emit_deny static) hold no double quote and no backslash.
# Needs command-lists.sh for the lists that some denials print.

# --- jq missing (all three hooks) ---
MSG_JQ_MISSING_REASON="The maddog guards require jq and it is not installed, so this call was denied rather than allowed unchecked. Install jq, then retry."
msg_jq_missing_context() {
  printf '%s' "Blocked by ${1}: jq is missing. STOP and return blocked to your caller, asking them to install jq - do not attempt the call."
}

# --- pattern-declare-guard.sh ---
MSG_PATTERN_REASON="write PATTERNS first, then repeat the call"
MSG_PATTERN_CONTEXT="Blocked by pattern-declare-guard.sh: your first message must hold a PATTERNS: line before your first tool call. Write it now (PATTERNS: <NAME>[, <NAME>], then one line per pattern that has a law), then repeat this call."

# --- judge-dispatch-guard.sh ---
WHY_EXECUTOR_JUDGE="this executor is fix-less by design and may only dispatch executor-fast-read or researcher, never a hand that changes anything — renting any hand to make a change is not permitted for executor-judge at all"
WHY_EXECUTOR_SMART="this executor may rent only the two cheap hands for work whose decisions it has closed; judgment, review, and research stay home or return to the caller"

# msg_dispatch_reason <caller> <target> <allowed-desc>
msg_dispatch_reason() {
  printf '%s' "Blocked by judge-dispatch-guard.sh: ${1} attempted to dispatch '${2}'. ${1} may only rent ${3} as hands."
}
# msg_dispatch_context <why>
msg_dispatch_context() {
  printf '%s' "Blocked by judge-dispatch-guard.sh: ${1}. STOP and return blocked (VERDICT: STOP for executor-judge) to your caller with this reason — do not attempt the dispatch."
}
# msg_no_target_reason <caller> <allowed-desc>
msg_no_target_reason() {
  printf '%s' "Blocked by judge-dispatch-guard.sh: ${1} attempted an Agent dispatch with no subagent_type named. Per the Agent tool contract, an absent, empty, or null subagent_type runs the default general-purpose agent, which holds every tool including Write and Edit. ${1} may only rent ${2} as hands."
}
# msg_no_target_context <why>
msg_no_target_context() {
  printf '%s' "Blocked by judge-dispatch-guard.sh: ${1}. Naming no subagent_type is not an exemption — it dispatches the unrestricted default agent. STOP and return blocked (VERDICT: STOP for executor-judge) to your caller with this reason — do not attempt the dispatch."
}

# --- executor-guard.sh: contexts ---
# A SHAPE refusal means the guard could not parse the command, so it refused it unread. That is
# not a ban, and a caller who obeys STOP would lose the whole command over a parse limit: the
# context tells every agent to rewrite as simpler separate commands and retry. SHAPE_CONTEXT is
# also the fail-closed backstop's context, which is static JSON.
SHAPE_CONTEXT="Blocked by executor-guard.sh: the guard could not parse this command, so it did not run. This is not a ban on what the command does. Rewrite it as simpler, separate commands (no leading '(' or '{' wrapper, full arguments for any wrapper such as timeout or stdbuf) and retry."
MSG_INTERNAL_ERROR_REASON="executor-guard.sh hit an internal error while inspecting this command, so it was denied rather than allowed unchecked. Rewrite it as simpler, separate commands and retry."

# msg_blocked_context <deny_writes 0|1> <is_judge 0|1>
# The context for every refusal that is not a shape refusal: STOP and return blocked. Only
# judge's text names its own verdict; only lead and judge are barred from writing files, so
# only their text says so.
msg_blocked_context() {
  local what="irreversible actions"
  [ "$1" -eq 1 ] && what="irreversible actions or write files via Bash"
  if [ "$2" -eq 1 ]; then
    printf '%s' "Blocked by executor-guard.sh: this executor is not permitted to weigh ${what}. STOP and return blocked (VERDICT: STOP) to your caller with this reason — do not attempt the command."
  else
    printf '%s' "Blocked by executor-guard.sh: this executor is not permitted to weigh ${what}. STOP and return blocked to your caller with this reason — do not attempt the command."
  fi
}

# --- executor-guard.sh: command shape (parse.sh) ---
MSG_SHAPE_PAREN="Cannot confidently identify the leading command — an unquoted '(' starts a subshell, arithmetic command, or command substitution used as the entire leading word, none of which this guard parses into. Rewrite without the wrapper."
MSG_SHAPE_BRACE="Cannot confidently identify the leading command — an unquoted '{' brace group is not parsed into by this guard. Rewrite without the wrapper."

# msg_wrapper_flag <wrapper> <flag>
msg_wrapper_flag() {
  printf '%s' "${1} with a flag (${2}) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command ${1} ends up running."
}
# msg_wrapper_missing <what is missing, e.g. "timeout -s is missing its argument">
msg_wrapper_missing() {
  printf '%s' "${1} — this guard's wrapper stripper cannot classify what runs next."
}

# --- executor-guard.sh: commands lead and judge cannot be shown to be read-only ---
# (rules-readonly.sh, and heredoc.sh for the heredoc one)
# msg_git_option <option>
msg_git_option() {
  printf '%s' "git with an option (${1}) before the subcommand is not understood by this guard, so it cannot tell which subcommand follows — denying rather than risk misclassifying a git write. Known global options: $(list_join ' ' "${GIT_OPTS_SHORT_VALUE[@]}" "${GIT_OPTS_VALUE[@]}" "${GIT_OPTS_FLAG[@]}")."
}
MSG_DYNAMIC_COMMAND="The command word is built from a variable or a command substitution, so this guard cannot tell which program runs and cannot classify it. Write the command name literally."
MSG_SUBST_UNBALANCED="A command substitution, backtick pair or process substitution is opened here but this guard cannot find where it ends, so it cannot read the command inside it. Close it, or run the inner command on its own."
MSG_SUBST_TOO_DEEP="Command substitutions are nested deeper than this guard reads, so it cannot classify the innermost command. Run the inner commands separately."
MSG_FUNCTION_DEF="A shell function definition (name() ..., name () ..., function name ...) hides what its body runs: this guard does not parse into a function body, so a shell or interpreter call inside it would go unchecked. This executor may not define shell functions via Bash; run each command directly."
MSG_HEREDOC_SUBST="A heredoc with an unquoted delimiter expands \$(...) and backticks in its body before the reader sees it, so a command placed there would run unchecked. Quote the delimiter (<<'EOF') or take the command substitution out of the body."

# --- executor-guard.sh: irreversible actions (rules-irreversible.sh) ---
MSG_RM_RECURSIVE="Recursive delete (rm -r/-R, with or without -f) targets a path outside a temp location — this can permanently destroy files with no undo."
MSG_FIND_DELETE="find with -delete permanently removes every matched file — irreversible."
MSG_PUSH_FORCE="git push with --force/--force-with-lease/-f can overwrite and permanently discard remote commit history — irreversible."
MSG_PUSH_PLUS="git push with a leading '+' refspec (e.g. +main) force-pushes and can overwrite remote commit history — irreversible."
MSG_CLEAN="git clean with -f combined with -d/-x permanently deletes untracked files and directories — irreversible."
MSG_RESET_HARD="git reset --hard permanently discards uncommitted changes and resets the working tree — irreversible."
MSG_CHECKOUT_DOT="git checkout of '.' mass-discards all uncommitted working-tree changes — irreversible."
MSG_RESTORE_DOT="git restore of '.' mass-discards uncommitted working-tree/staged changes — irreversible."
MSG_BRANCH_D="git branch -D force-deletes a branch and can drop unmerged commits — irreversible."
MSG_BRANCH_DELETE_FORCE="git branch --delete/-d combined with --force/-f force-deletes a branch and can drop unmerged commits — irreversible."
MSG_MERGE="git merge (including --no-ff/--squash/-m forms) lands one branch's history into another — landing a merge is the user's hand alone, not this executor's, and it is a one-way door once pushed. Use --abort/--continue only to recover from a merge already in progress."
MSG_WORKTREE_REMOVE="git worktree remove deletes a worktree and can discard uncommitted work inside it — irreversible."
MSG_WORKTREE_PRUNE="git worktree prune permanently deletes administrative data for worktrees git decides are stale — irreversible."
# msg_publish <package manager>
msg_publish() {
  printf '%s' "${1} publish pushes a package version live to the registry — cannot be cleanly unpublished."
}

# --- executor-guard.sh: file writes by lead and judge (rules-readonly.sh) ---
MSG_RM_FILE="rm deletes a file — this executor may not write, create, move, or delete files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
# msg_shell <shell>
msg_shell() {
  printf '%s' "${1} is a shell invocation — this guard does not parse a shell's own -c argument or script as a nested command line, so it cannot classify what runs inside it; running a shell here would launder any write-form or interpreter invocation past every check in this file. This executor may not invoke a shell via Bash."
}
# msg_write_cmd <command>
msg_write_cmd() {
  printf '%s' "${1} creates, overwrites, or moves a file — this executor may not write files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
}
# msg_interpreter <command>
msg_interpreter() {
  printf '%s' "${1} is an inline interpreter or scripting tool this executor may not run via Bash — Bash is read-only here ($(list_join / "${READONLY_CMDS[@]}") cover inspection); route scripted or destructive work through an executor that holds Write/Edit."
}
MSG_SED_INPLACE="sed -i edits a file in place — this executor may not write files via Bash."
MSG_DD_OUTPUT="dd of= writes/overwrites a file — this executor may not write files via Bash."
MSG_AWK_REDIRECT="awk with an embedded '>' likely redirects output to a file — this executor may not write files via Bash."
# msg_git_write <git subcommand>
msg_git_write() {
  printf '%s' "git ${1} changes tracked/staged file state — this executor may not write files via Bash."
}
MSG_GIT_RESTORE="git restore overwrites working-tree/staged files from another version — this executor may not write files via Bash."
MSG_GIT_CHECKOUT_PATH="git checkout -- restores file contents from another version, discarding working-tree edits — this executor may not write files via Bash."
MSG_REDIRECT="output redirection (>, >>, &>) writes to a file — this executor may not write files via Bash."
# The allowed-forms tail both git tag denials print.
_msg_tag_allowed() {
  printf '%s' "only listing and verifying tags ($(list_join ', ' "${GIT_TAG_READ_FORMS[@]}")) is allowed."
}
# msg_tag_flag <flag>
msg_tag_flag() {
  printf '%s' "git tag with '${1}' can create, delete or move a tag — this executor may not write via Bash; $(_msg_tag_allowed)"
}
msg_tag_name() {
  printf '%s' "git tag with a tag name creates a tag — this executor may not write via Bash; $(_msg_tag_allowed)"
}
