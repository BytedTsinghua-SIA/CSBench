set (CMAKE_CXX_STANDARD 23)
set (CMAKE_EXPORT_COMPILE_COMMANDS ON)

if (MSVC)
	# MSVC uses different flag syntax; keep it warning-rich but compatible.
	set(SANITIZING_FLAGS "")
	set (CMAKE_BASE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
else()
	set(SANITIZING_FLAGS -fno-sanitize-recover=all -fsanitize=undefined -fsanitize=address)

	# ask for more warnings from the compiler
	set (CMAKE_BASE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wpedantic -Wextra -Weffc++ -Werror -Wshadow -Wpointer-arith -Wcast-qual -Wformat=2 -Wno-unqualified-std-cast-call -Wno-non-virtual-dtor")
endif()
