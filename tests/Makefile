-include ../Makefile

f?=Code

lua: docs2lua $f.lua ## run a tests/*.lua file; e.g. make f="Numsym" lua
	LUA_PATH='../src/?.lua;;' lua $f.lua


