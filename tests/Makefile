# Default is to run a test e.g
#
#    make 
#    make f=Data
#
# will update and run tests/Code.lua (first call) or  tests/Data.lua (second call).

f?=Code

lua: docs2lua $f.lua ## run a tests/*.lua file; e.g. make f="Numsym" lua
	LUA_PATH='../src/?.lua;;' lua $f.lua

-include ../Makefile

