#!/usr/bin/osascript
on run arguments
    set promptText to item 1 of arguments
    set response to display dialog promptText with title "Sherlock SSH authentication" default answer "" with hidden answer buttons {"Cancel", "Continue"} default button "Continue" cancel button "Cancel" giving up after 180
    if gave up of response then error number -128
    return text returned of response
end run
