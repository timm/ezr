# Default is to run a test e.g
#
#    make 
#    make f=Data
#
# will update and run tests/Code.lua (first call) or  tests/Data.lua (second call).


eg?=data

testLua: $(eg).lua  ## run a tests/*.lua file; e.g. make eg=data
	LUA_PATH='../src/?.lua;;' lua $(eg).lua
	rm $(eg).lua

clean:
		rm *.lua

-include ../Makefile

