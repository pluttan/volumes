# vol(1) fish completion

function __vol_complete
    vol --completion 2>/dev/null | string split ' '
end

complete -c vol -f -a '(__vol_complete)'
