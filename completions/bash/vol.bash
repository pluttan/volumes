# vol(1) bash completion

_vol() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local commands
    commands=$(vol --completion 2>/dev/null)
    COMPREPLY=($(compgen -W "$commands" -- "$cur"))
}

complete -F _vol vol
