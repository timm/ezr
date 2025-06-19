#!/bin/env bash
me=`basename $PWD`
me=${me^^}
bold=$(tput bold)
col1=$(tput setaf 6)
col2=$(tput setaf 3)
col0=$(tput sgr0)
meme="${bold}${col1}$me${col0}"

hi() { 
  clear
  echo -n "$bold$col1"; figlet -W -f slant "$me"; echo -n $col0
  echo -n $col2; aliases; echo -n $col0; }

aliases() {
  echo "Short cuts:"
  alias | sed 's/alias /  /'
  echo ""; }

there() { 
  cd $1; basename `pwd`; }

alias ..='cd ..'
alias ...='cd ../../../'
alias h="history"
alias ls="ls -G"
alias py="python3 -B "
alias vi="nvim -u $Top/etc/init.lua"

pretty() {
  gawk -F, '
  FNR==NR {
    for (i=1; i<=NF; i++)
      if (length($i) > width[i]) width[i] = length($i)
    next }
  { for (i=1; i<=NF; i++) {
      printf "%-*s", width[i], $i
      if (i < NF) printf ", " }
    print "" }
  ' "$1" "$1"
}


export BASH_SILENCE_DEPRECATION_WARNING=1
#export PATH="$PWD:/opt/homebrew/bin:$PATH"
#export PATH="$PWD:/Library/Frameworks/Python.framework/Versions/3.13/bin:$PATH"

EDITOR=nvim

PROMPT_COMMAND='echo -ne "${meme}! $(git branch 2>/dev/null | grep '\''^*'\'' | colrm 1 2):";PS1="$(there ..)/$(there .):\!\e[m ▶ "'
hi
